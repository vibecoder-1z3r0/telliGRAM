"""Enhanced timeline editor widget for animation sequences"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QSlider, QCheckBox, QSpinBox, QFrame, QComboBox,
    QLineEdit, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap

from telligram.core.project import Project
from telligram.core.animation import Animation


class FrameThumbnail(QFrame):
    """Visual thumbnail for a single frame in the timeline"""

    clicked = Signal(int)  # Emits frame index when clicked
    duration_changed = Signal(int, int)  # Emits (frame_index, new_duration)
    remove_requested = Signal(int)  # Emits frame index to remove

    def __init__(self, frame_index: int):
        super().__init__()
        self.frame_index = frame_index
        self.card_slot = None
        self.project = None
        self.is_current = False

        self.setFixedSize(90, 130)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Frame number label
        self.index_label = QLabel(f"#{frame_index + 1}")
        self.index_label.setAlignment(Qt.AlignCenter)
        self.index_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.index_label)

        # Card preview (rendered in paintEvent)
        self.preview_widget = QWidget()
        self.preview_widget.setFixedSize(70, 70)
        layout.addWidget(self.preview_widget, alignment=Qt.AlignCenter)

        # Card slot label
        self.slot_label = QLabel("Slot 0")
        self.slot_label.setAlignment(Qt.AlignCenter)
        self.slot_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(self.slot_label)

        # Duration spinbox
        dur_layout = QHBoxLayout()
        dur_layout.addWidget(QLabel("Dur:"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(1)
        self.duration_spin.setMaximum(99)
        self.duration_spin.setValue(5)
        self.duration_spin.setFixedWidth(50)
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        dur_layout.addWidget(self.duration_spin)
        layout.addLayout(dur_layout)

        self._update_style()

    def set_frame_data(self, card_slot: int, duration: int, project: Project):
        """Set frame data"""
        self.card_slot = card_slot
        self.project = project
        self.duration_spin.setValue(duration)
        self.slot_label.setText(f"Slot {card_slot}")
        self.update()

    def set_frame_index(self, index: int):
        """Update frame index label"""
        self.frame_index = index
        self.index_label.setText(f"#{index + 1}")

    def set_current(self, is_current: bool):
        """Highlight as current frame during playback"""
        self.is_current = is_current
        self._update_style()

    def _update_style(self):
        """Update visual style"""
        if self.is_current:
            self.setStyleSheet("""
                QFrame {
                    background-color: #0078D4;
                    border: 3px solid #0078D4;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #3c3c3c;
                }
                QFrame:hover {
                    border: 1px solid #666;
                }
            """)

    def _on_duration_changed(self, value):
        """Emit duration change signal"""
        self.duration_changed.emit(self.frame_index, value)

    def mousePressEvent(self, event):
        """Handle click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.frame_index)

    def contextMenuEvent(self, event):
        """Handle right-click"""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction

        menu = QMenu(self)
        remove_action = QAction("Remove Frame", self)
        remove_action.triggered.connect(lambda: self.remove_requested.emit(self.frame_index))
        menu.addAction(remove_action)
        menu.exec(event.globalPos())

    def paintEvent(self, event):
        """Paint card preview"""
        super().paintEvent(event)

        if self.project is None or self.card_slot is None:
            return

        card = self.project.get_card(self.card_slot)
        if card is None:
            return

        # Draw card preview on preview_widget
        painter = QPainter(self)

        # Calculate preview area (70x70)
        preview_x = 10
        preview_y = 25
        preview_size = 70
        pixel_size = preview_size // 8

        # Draw background
        painter.fillRect(preview_x, preview_y, preview_size, preview_size, QColor("#1a1a1a"))

        # Draw pixels
        for y in range(8):
            for x in range(8):
                if card.get_pixel(x, y):
                    painter.fillRect(
                        preview_x + x * pixel_size,
                        preview_y + y * pixel_size,
                        pixel_size,
                        pixel_size,
                        QColor("#FFFFFF")
                    )

        # Draw grid
        painter.setPen(QPen(QColor("#333"), 1))
        for i in range(9):
            # Vertical lines
            x = preview_x + i * pixel_size
            painter.drawLine(x, preview_y, x, preview_y + preview_size)
            # Horizontal lines
            y = preview_y + i * pixel_size
            painter.drawLine(preview_x, y, preview_x + preview_size, y)


class TimelineEditorWidget(QWidget):
    """Enhanced timeline editor with visual preview and full controls"""

    animation_changed = Signal()  # Emitted when animation is modified

    def __init__(self):
        super().__init__()
        self.project = None
        self.current_animation = None
        self.current_card_slot = 0
        self.frame_thumbnails = []
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._advance_frame)
        self.current_playback_frame = 0
        self.is_playing = False

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Animation manager section
        anim_header = QHBoxLayout()
        anim_header.addWidget(QLabel("<b>Animation:</b>"))

        self.animation_combo = QComboBox()
        self.animation_combo.setMinimumWidth(200)
        self.animation_combo.currentIndexChanged.connect(self._on_animation_selected)
        anim_header.addWidget(self.animation_combo, stretch=1)

        self.new_anim_btn = QPushButton("New")
        self.new_anim_btn.clicked.connect(self._new_animation)
        anim_header.addWidget(self.new_anim_btn)

        self.rename_anim_btn = QPushButton("Rename")
        self.rename_anim_btn.clicked.connect(self._rename_animation)
        anim_header.addWidget(self.rename_anim_btn)

        self.delete_anim_btn = QPushButton("Delete")
        self.delete_anim_btn.clicked.connect(self._delete_animation)
        anim_header.addWidget(self.delete_anim_btn)

        layout.addLayout(anim_header)

        # Timeline scroll area
        timeline_label = QLabel("<b>Timeline:</b>")
        layout.addWidget(timeline_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(160)
        scroll.setMaximumHeight(160)

        self.timeline_widget = QWidget()
        self.timeline_layout = QHBoxLayout(self.timeline_widget)
        self.timeline_layout.setContentsMargins(5, 5, 5, 5)
        self.timeline_layout.setSpacing(5)
        self.timeline_layout.addStretch()

        scroll.setWidget(self.timeline_widget)
        layout.addWidget(scroll)

        # Frame controls
        frame_controls = QHBoxLayout()

        self.add_frame_btn = QPushButton("Add Current Card")
        self.add_frame_btn.clicked.connect(self._add_current_card)
        frame_controls.addWidget(self.add_frame_btn)

        self.insert_frame_btn = QPushButton("Insert Before Selected")
        self.insert_frame_btn.clicked.connect(self._insert_frame)
        frame_controls.addWidget(self.insert_frame_btn)

        frame_controls.addStretch()

        layout.addLayout(frame_controls)

        # Playback controls
        playback_controls = QHBoxLayout()

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setMinimumWidth(80)
        self.play_btn.clicked.connect(self._toggle_playback)
        playback_controls.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self._stop_playback)
        playback_controls.addWidget(self.stop_btn)

        self.rewind_btn = QPushButton("⏮ Rewind")
        self.rewind_btn.clicked.connect(self._rewind)
        playback_controls.addWidget(self.rewind_btn)

        playback_controls.addWidget(QLabel("|"))

        self.loop_checkbox = QCheckBox("Loop")
        self.loop_checkbox.stateChanged.connect(self._on_loop_changed)
        playback_controls.addWidget(self.loop_checkbox)

        playback_controls.addWidget(QLabel("|"))

        playback_controls.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(60)
        self.speed_slider.setValue(60)
        self.speed_slider.setFixedWidth(150)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        playback_controls.addWidget(self.speed_slider)

        self.speed_label = QLabel("60 fps")
        self.speed_label.setFixedWidth(50)
        playback_controls.addWidget(self.speed_label)

        playback_controls.addStretch()

        self.playback_info_label = QLabel("Frame: 0 / 0")
        playback_controls.addWidget(self.playback_info_label)

        layout.addLayout(playback_controls)

    def set_project(self, project: Project):
        """Set project"""
        self.project = project
        self._refresh_animation_list()
        if len(project.animations) > 0:
            self.animation_combo.setCurrentIndex(0)
        else:
            self._load_animation(None)

    def set_current_card_slot(self, slot: int):
        """Set currently selected card slot"""
        self.current_card_slot = slot

    def _refresh_animation_list(self):
        """Refresh animation combo box"""
        self.animation_combo.blockSignals(True)
        current_name = self.current_animation.name if self.current_animation else None
        self.animation_combo.clear()

        if self.project:
            for i, anim in enumerate(self.project.animations):
                self.animation_combo.addItem(f"{anim.name} ({anim.frame_count} frames)")
                if self.current_animation and anim.name == current_name:
                    self.animation_combo.setCurrentIndex(i)

        self.animation_combo.blockSignals(False)

    def _on_animation_selected(self, index):
        """Handle animation selection"""
        if self.project and 0 <= index < len(self.project.animations):
            self._load_animation(self.project.animations[index])
        else:
            self._load_animation(None)

    def _load_animation(self, animation: Animation):
        """Load animation into timeline"""
        self.current_animation = animation
        self._stop_playback()

        # Clear existing thumbnails
        for thumb in self.frame_thumbnails:
            self.timeline_layout.removeWidget(thumb)
            thumb.deleteLater()
        self.frame_thumbnails.clear()

        if animation is None:
            self._update_playback_info()
            return

        # Create thumbnails for each frame
        for i in range(animation.frame_count):
            self._create_frame_thumbnail(i)

        # Update controls
        self.loop_checkbox.setChecked(animation.loop)
        self.speed_slider.setValue(animation.fps)
        self._update_playback_info()

    def _create_frame_thumbnail(self, index):
        """Create a single frame thumbnail"""
        if not self.current_animation:
            return

        frame_data = self.current_animation.get_frame(index)
        thumb = FrameThumbnail(index)
        thumb.set_frame_data(frame_data["card_slot"], frame_data["duration"], self.project)
        thumb.clicked.connect(self._on_frame_clicked)
        thumb.duration_changed.connect(self._on_frame_duration_changed)
        thumb.remove_requested.connect(self._remove_frame_at)

        # Insert before stretch
        self.timeline_layout.insertWidget(index, thumb)
        self.frame_thumbnails.append(thumb)

    def _update_frame_indices(self):
        """Update frame index labels after insert/remove"""
        for i, thumb in enumerate(self.frame_thumbnails):
            thumb.set_frame_index(i)

    def _new_animation(self):
        """Create new animation"""
        if not self.project:
            return

        name, ok = QInputDialog.getText(self, "New Animation", "Animation name:")
        if not ok or not name:
            return

        anim = Animation(name=name)  # Uses default fps=60, loop=False
        self.project.add_animation(anim)

        self._refresh_animation_list()
        self.animation_combo.setCurrentIndex(len(self.project.animations) - 1)
        self.animation_changed.emit()

    def _rename_animation(self):
        """Rename current animation"""
        if not self.current_animation:
            return

        name, ok = QInputDialog.getText(self, "Rename Animation", "New name:", text=self.current_animation.name)
        if ok and name:
            self.current_animation.name = name
            self._refresh_animation_list()
            self.animation_changed.emit()

    def _delete_animation(self):
        """Delete current animation"""
        if not self.current_animation or not self.project:
            return

        reply = QMessageBox.question(
            self,
            "Delete Animation",
            f"Delete animation '{self.current_animation.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.project.animations.remove(self.current_animation)
            self._refresh_animation_list()

            if len(self.project.animations) > 0:
                self.animation_combo.setCurrentIndex(0)
            else:
                self._load_animation(None)

            self.animation_changed.emit()

    def _add_current_card(self):
        """Add current card to end of animation"""
        if not self.current_animation:
            return

        self.current_animation.add_frame(card_slot=self.current_card_slot, duration=5)
        self._create_frame_thumbnail(self.current_animation.frame_count - 1)
        self._refresh_animation_list()
        self._update_playback_info()
        self.animation_changed.emit()

    def _insert_frame(self):
        """Insert current card before selected frame"""
        if not self.current_animation or len(self.frame_thumbnails) == 0:
            self._add_current_card()
            return

        # Find selected frame (or use 0)
        selected_index = 0
        for i, thumb in enumerate(self.frame_thumbnails):
            if thumb.is_current:
                selected_index = i
                break

        self.current_animation.insert_frame(selected_index, self.current_card_slot, duration=5)
        self._load_animation(self.current_animation)  # Reload to rebuild thumbnails
        self._refresh_animation_list()
        self.animation_changed.emit()

    def _remove_frame_at(self, index):
        """Remove frame at index"""
        if not self.current_animation or index >= self.current_animation.frame_count:
            return

        self.current_animation.remove_frame(index)
        self._load_animation(self.current_animation)  # Reload
        self._refresh_animation_list()
        self._update_playback_info()
        self.animation_changed.emit()

    def _on_frame_clicked(self, frame_index):
        """Handle frame click - jump to frame in playback"""
        self.current_playback_frame = frame_index
        self._update_current_frame_highlight()
        self._update_playback_info()

    def _on_frame_duration_changed(self, frame_index, new_duration):
        """Handle duration change"""
        if not self.current_animation or frame_index >= self.current_animation.frame_count:
            return

        frame = self.current_animation.get_frame(frame_index)
        frame["duration"] = new_duration
        self._update_playback_info()
        self.animation_changed.emit()

    def _on_speed_changed(self, fps):
        """Handle speed slider change"""
        self.speed_label.setText(f"{fps} fps")
        if self.current_animation:
            self.current_animation.fps = fps
            if self.is_playing:
                self._update_playback_timer()
            self.animation_changed.emit()

    def _on_loop_changed(self, state):
        """Handle loop checkbox change"""
        if self.current_animation:
            self.current_animation.loop = (state == Qt.Checked)
            self.animation_changed.emit()

    def _toggle_playback(self):
        """Toggle play/pause"""
        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        """Start playback"""
        if not self.current_animation or self.current_animation.frame_count == 0:
            return

        self.is_playing = True
        self.play_btn.setText("⏸ Pause")
        self._update_playback_timer()
        self.playback_timer.start()

    def _pause_playback(self):
        """Pause playback"""
        self.is_playing = False
        self.play_btn.setText("▶ Play")
        self.playback_timer.stop()

    def _stop_playback(self):
        """Stop playback and rewind"""
        self._pause_playback()
        self.current_playback_frame = 0
        self._update_current_frame_highlight()
        self._update_playback_info()

    def _rewind(self):
        """Rewind to start"""
        self.current_playback_frame = 0
        self._update_current_frame_highlight()
        self._update_playback_info()

    def _update_playback_timer(self):
        """Update timer interval based on FPS"""
        if self.current_animation:
            interval_ms = int(1000 / self.current_animation.fps)
            self.playback_timer.setInterval(interval_ms)

    def _advance_frame(self):
        """Advance to next frame during playback"""
        if not self.current_animation:
            return

        self.current_playback_frame += 1

        # Check if reached end
        if self.current_playback_frame >= self.current_animation.frame_count:
            if self.current_animation.loop:
                self.current_playback_frame = 0
            else:
                self._stop_playback()
                return

        self._update_current_frame_highlight()
        self._update_playback_info()

    def _update_current_frame_highlight(self):
        """Update which frame is highlighted as current"""
        for i, thumb in enumerate(self.frame_thumbnails):
            thumb.set_current(i == self.current_playback_frame)

    def _update_playback_info(self):
        """Update playback info label"""
        if self.current_animation:
            total = self.current_animation.frame_count
            self.playback_info_label.setText(f"Frame: {self.current_playback_frame + 1} / {total}")
        else:
            self.playback_info_label.setText("Frame: 0 / 0")
