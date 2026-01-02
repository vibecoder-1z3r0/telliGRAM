"""Enhanced timeline editor widget for animation sequences"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QSlider, QCheckBox, QSpinBox, QFrame, QComboBox,
    QLineEdit, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QMimeData, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QDrag

from telligram.core.project import Project
from telligram.core.animation import Animation
from telligram.core.constants import get_color_hex, COLOR_NAMES


class FrameThumbnail(QFrame):
    """Visual thumbnail for a single frame in the timeline"""

    clicked = Signal(int)  # Emits frame index when clicked
    duration_changed = Signal(int, int)  # Emits (frame_index, new_duration)
    remove_requested = Signal(int)  # Emits frame index to remove
    reorder_requested = Signal(int, int)  # Emits (from_index, to_index)
    duplicate_requested = Signal(int)  # Emits frame index to duplicate

    def __init__(self, frame_index: int):
        super().__init__()
        self.frame_index = frame_index
        self.card_slot = None
        self.project = None
        self.is_current = False
        self.drag_start_pos = None

        self.setFixedSize(90, 130)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setAcceptDrops(True)

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
        self.slot_label.setText(f"Card {card_slot}")
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
        """Handle click and drag start"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.clicked.emit(self.frame_index)

    def mouseMoveEvent(self, event):
        """Handle drag"""
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.drag_start_pos is None:
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < 10:
            return

        # Start drag operation
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.frame_index))
        drag.setMimeData(mime_data)
        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        """Accept drag enter"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Accept drag move"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop - emit signal"""
        if event.mimeData().hasText():
            from_index = int(event.mimeData().text())
            to_index = self.frame_index
            self.reorder_requested.emit(from_index, to_index)
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        """Handle right-click"""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction

        menu = QMenu(self)

        # Move actions
        move_left_action = QAction("Move Left", self)
        move_left_action.triggered.connect(lambda: self.reorder_requested.emit(self.frame_index, self.frame_index - 1))
        move_left_action.setEnabled(self.frame_index > 0)
        menu.addAction(move_left_action)

        move_right_action = QAction("Move Right", self)
        move_right_action.triggered.connect(lambda: self.reorder_requested.emit(self.frame_index, self.frame_index + 1))
        # Enable will be checked by parent
        menu.addAction(move_right_action)

        menu.addSeparator()

        duplicate_action = QAction("Duplicate Card", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_requested.emit(self.frame_index))
        menu.addAction(duplicate_action)

        menu.addSeparator()

        remove_action = QAction("Remove Card", self)
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

        # Get card color
        card_color = get_color_hex(card.color) if hasattr(card, 'color') else "#FFFFFF"

        # Draw pixels
        for y in range(8):
            for x in range(8):
                if card.get_pixel(x, y):
                    painter.fillRect(
                        preview_x + x * pixel_size,
                        preview_y + y * pixel_size,
                        pixel_size,
                        pixel_size,
                        QColor(card_color)
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


class AnimationPreviewWidget(QFrame):
    """Preview widget showing the current animation frame"""

    def __init__(self):
        super().__init__()
        self.project = None
        self.current_card_slot = None
        self.color_override = None  # None or color index 0-15
        self.setFixedSize(200, 200)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background-color: #1a1a1a; border: 2px solid #3c3c3c;")

    def set_card(self, card_slot: int, project, color_override=None):
        """Set the card to display"""
        self.current_card_slot = card_slot
        self.project = project
        self.color_override = color_override
        self.update()

    def clear(self):
        """Clear the preview"""
        self.current_card_slot = None
        self.update()

    def paintEvent(self, event):
        """Paint the card preview"""
        super().paintEvent(event)

        painter = QPainter(self)

        if self.project is None or self.current_card_slot is None:
            # Draw "no animation" text
            painter.setPen(QColor("#888"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No Preview")
            return

        card = self.project.get_card(self.current_card_slot)
        if card is None:
            painter.setPen(QColor("#888"))
            painter.drawText(self.rect(), Qt.AlignCenter, f"Card {self.current_card_slot}\nEmpty")
            return

        # Draw card preview (160x160 centered)
        preview_size = 160
        pixel_size = preview_size // 8
        offset_x = (200 - preview_size) // 2
        offset_y = (200 - preview_size) // 2

        # Draw background
        painter.fillRect(offset_x, offset_y, preview_size, preview_size, QColor("#1a1a1a"))

        # Get card color - use override if set
        if self.color_override is not None:
            card_color = get_color_hex(self.color_override)
        else:
            card_color = get_color_hex(card.color) if hasattr(card, 'color') else "#FFFFFF"

        # Draw pixels
        for y in range(8):
            for x in range(8):
                if card.get_pixel(x, y):
                    painter.fillRect(
                        offset_x + x * pixel_size,
                        offset_y + y * pixel_size,
                        pixel_size,
                        pixel_size,
                        QColor(card_color)
                    )

        # Draw grid
        painter.setPen(QPen(QColor("#444"), 1))
        for i in range(9):
            # Vertical lines
            x = offset_x + i * pixel_size
            painter.drawLine(x, offset_y, x, offset_y + preview_size)
            # Horizontal lines
            y = offset_y + i * pixel_size
            painter.drawLine(offset_x, y, offset_x + preview_size, y)


class TimelineEditorWidget(QWidget):
    """Enhanced timeline editor with visual preview and full controls"""

    animation_changed = Signal()  # Emitted when animation is modified

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.project = None
        self.current_animation = None
        self.current_card_slot = 0
        self.current_color_override = None  # None means use original colors
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
        layout.setSpacing(3)  # Reduce spacing between sections

        # Animation manager section
        anim_header = QHBoxLayout()
        anim_header.setSpacing(5)
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

        # Timeline label
        timeline_label = QLabel("<b>Timeline:</b>")
        layout.addWidget(timeline_label)

        # Playback controls (above timeline)
        playback_controls = QHBoxLayout()
        playback_controls.setSpacing(5)

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

        # Horizontal layout for timeline + preview
        main_content = QHBoxLayout()
        main_content.setSpacing(10)

        # Left side: Timeline scroll area + frame controls
        timeline_section = QVBoxLayout()
        timeline_section.setSpacing(3)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(160)
        scroll.setMaximumHeight(160)
        scroll.setMinimumWidth(400)  # Shrink timeline horizontally

        self.timeline_widget = QWidget()
        self.timeline_layout = QHBoxLayout(self.timeline_widget)
        self.timeline_layout.setContentsMargins(5, 5, 5, 5)
        self.timeline_layout.setSpacing(5)
        self.timeline_layout.addStretch()

        scroll.setWidget(self.timeline_widget)
        timeline_section.addWidget(scroll)

        # Frame controls below timeline
        frame_controls = QHBoxLayout()
        frame_controls.setSpacing(5)

        self.add_frame_btn = QPushButton("Add Card")
        self.add_frame_btn.clicked.connect(self._add_current_card)
        frame_controls.addWidget(self.add_frame_btn)

        self.insert_frame_btn = QPushButton("Insert Card")
        self.insert_frame_btn.clicked.connect(self._insert_frame)
        frame_controls.addWidget(self.insert_frame_btn)

        frame_controls.addWidget(QLabel("|"))

        self.move_left_btn = QPushButton("◀ Move Left")
        self.move_left_btn.clicked.connect(self._move_selected_left)
        frame_controls.addWidget(self.move_left_btn)

        self.move_right_btn = QPushButton("Move Right ▶")
        self.move_right_btn.clicked.connect(self._move_selected_right)
        frame_controls.addWidget(self.move_right_btn)

        frame_controls.addWidget(QLabel("|"))

        self.color_override_combo = QComboBox()
        self.color_override_combo.addItem("Original")
        for color_name in COLOR_NAMES:
            self.color_override_combo.addItem(color_name)
        self.color_override_combo.setCurrentIndex(0)
        self.color_override_combo.currentIndexChanged.connect(self._on_color_override_changed)
        frame_controls.addWidget(self.color_override_combo)

        frame_controls.addStretch()

        timeline_section.addLayout(frame_controls)
        main_content.addLayout(timeline_section, stretch=1)

        # Right side: Preview widget
        preview_section = QVBoxLayout()
        preview_section.setSpacing(3)

        self.preview_widget = AnimationPreviewWidget()
        preview_section.addWidget(self.preview_widget, alignment=Qt.AlignTop)

        main_content.addLayout(preview_section, stretch=0)

        layout.addLayout(main_content)
        layout.addStretch()  # Push everything to the top

    def set_project(self, project: Project):
        """Set project"""
        self.project = project
        self._refresh_animation_list()
        # Don't auto-select an animation - user should choose explicitly
        self._load_animation(None)

    def set_current_card_slot(self, slot: int):
        """Set currently selected card slot"""
        self.current_card_slot = slot

    def _refresh_animation_list(self):
        """Refresh animation combo box"""
        self.animation_combo.blockSignals(True)
        current_name = self.current_animation.name if self.current_animation else None
        self.animation_combo.clear()

        # Add placeholder for "no selection"
        self.animation_combo.addItem("(Select Animation)")

        if self.project:
            for i, anim in enumerate(self.project.animations):
                self.animation_combo.addItem(f"{anim.name} ({anim.frame_count} frames)")
                if self.current_animation and anim.name == current_name:
                    self.animation_combo.setCurrentIndex(i + 1)  # +1 for placeholder

        # If no current animation, select placeholder
        if not self.current_animation:
            self.animation_combo.setCurrentIndex(0)

        self.animation_combo.blockSignals(False)

    def _on_animation_selected(self, index):
        """Handle animation selection"""
        # Index 0 is the placeholder "(Select Animation)"
        if index == 0 or not self.project:
            self._load_animation(None)
        else:
            # Adjust for placeholder offset
            anim_index = index - 1
            if 0 <= anim_index < len(self.project.animations):
                self._load_animation(self.project.animations[anim_index])
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
            self._update_button_states()
            return

        # Create thumbnails for each frame
        for i in range(animation.frame_count):
            self._create_frame_thumbnail(i)

        # Update controls
        self.loop_checkbox.setChecked(animation.loop)
        self.speed_slider.setValue(animation.fps)
        self._update_playback_info()
        self._update_button_states()

    def _update_button_states(self):
        """Enable/disable buttons based on whether an animation is loaded"""
        has_animation = self.current_animation is not None

        # Playback controls
        self.play_btn.setEnabled(has_animation)
        self.stop_btn.setEnabled(has_animation)
        self.rewind_btn.setEnabled(has_animation)
        self.loop_checkbox.setEnabled(has_animation)
        self.speed_slider.setEnabled(has_animation)

        # Frame manipulation controls
        self.add_frame_btn.setEnabled(has_animation)
        self.insert_frame_btn.setEnabled(has_animation)
        self.move_left_btn.setEnabled(has_animation)
        self.move_right_btn.setEnabled(has_animation)
        self.color_override_combo.setEnabled(has_animation)

        # Animation management controls
        self.rename_anim_btn.setEnabled(has_animation)
        self.delete_anim_btn.setEnabled(has_animation)

        # New button and combo are always enabled (no change needed)

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
        thumb.reorder_requested.connect(self._reorder_frames)
        thumb.duplicate_requested.connect(self._duplicate_frame)

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

        # Use undoable command if main_window available
        if self.main_window:
            self.main_window.create_animation_undoable(name)
        else:
            # Fallback for direct use without main_window
            anim = Animation(name=name)
            self.project.add_animation(anim)
            self._refresh_animation_list()
            self.animation_combo.setCurrentIndex(len(self.project.animations) - 1)
            self.animation_changed.emit()

    def _rename_animation(self):
        """Rename current animation"""
        if not self.current_animation:
            return

        old_name = self.current_animation.name
        name, ok = QInputDialog.getText(self, "Rename Animation", "New name:", text=old_name)
        if ok and name and name != old_name:
            # Use undoable command if main_window available
            if self.main_window:
                self.main_window.rename_animation_undoable(self.current_animation, old_name, name)
            else:
                # Fallback
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
            # Find current index before deletion
            current_index = self.project.animations.index(self.current_animation)

            # Use undoable command if main_window available
            if self.main_window:
                self.main_window.delete_animation_undoable(self.current_animation, current_index)
            else:
                # Fallback
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
            # No animation selected - create a default one
            if not self.project:
                return

            if self.main_window:
                anim = self.main_window.create_animation_undoable("Animation 1")
                self.current_animation = anim
            else:
                # Fallback
                anim = Animation(name="Animation 1")
                self.project.add_animation(anim)
                self._refresh_animation_list()
                self.animation_combo.setCurrentIndex(0)
                self._load_animation(anim)

        # Use undoable command if main_window available
        if self.main_window:
            self.main_window.add_frame_undoable(self.current_animation, self.current_card_slot, 5)
        else:
            # Fallback
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

        # Use undoable command if main_window available
        if self.main_window:
            self.main_window.insert_frame_undoable(self.current_animation, selected_index, self.current_card_slot, 5)
        else:
            # Fallback
            self.current_animation.insert_frame(selected_index, self.current_card_slot, duration=5)
            self._load_animation(self.current_animation)
            self._refresh_animation_list()
            self.animation_changed.emit()

    def _remove_frame_at(self, index):
        """Remove frame at index"""
        if not self.current_animation or index >= self.current_animation.frame_count:
            return

        # Use undoable command if main_window available
        if self.main_window:
            self.main_window.remove_frame_undoable(self.current_animation, index)
        else:
            # Fallback
            self.current_animation.remove_frame(index)
            self._load_animation(self.current_animation)
            self._refresh_animation_list()
            self._update_playback_info()
            self.animation_changed.emit()

    def _on_frame_clicked(self, frame_index):
        """Handle frame click - jump to frame in playback"""
        self.current_playback_frame = frame_index
        self._update_current_frame_highlight()
        self._update_playback_info()
        self._update_preview()

    def _on_frame_duration_changed(self, frame_index, new_duration):
        """Handle duration change"""
        if not self.current_animation or frame_index >= self.current_animation.frame_count:
            return

        frame = self.current_animation.get_frame(frame_index)
        old_duration = frame["duration"]

        if old_duration != new_duration:
            # Use undoable command if main_window available
            if self.main_window:
                self.main_window.change_frame_duration_undoable(
                    self.current_animation, frame_index, old_duration, new_duration
                )
            else:
                # Fallback
                frame["duration"] = new_duration
                self._update_playback_info()
                self.animation_changed.emit()

    def _reorder_frames(self, from_index: int, to_index: int):
        """Reorder frames in timeline"""
        if not self.current_animation:
            return
        if from_index == to_index:
            return

        # Use undoable command if main_window available
        if self.main_window:
            self.main_window.reorder_frame_undoable(self.current_animation, from_index, to_index)
        else:
            # Fallback
            frame = self.current_animation._frames.pop(from_index)
            self.current_animation._frames.insert(to_index, frame)
            self._load_animation(self.current_animation)
            self.animation_changed.emit()

    def _duplicate_frame(self, index: int):
        """Duplicate a frame"""
        if not self.current_animation or index >= self.current_animation.frame_count:
            return

        # Use undoable command if main_window available
        if self.main_window:
            self.main_window.duplicate_frame_undoable(self.current_animation, index)
        else:
            # Fallback
            frame = self.current_animation.get_frame(index)
            self.current_animation.insert_frame(index + 1, frame["card_slot"], frame["duration"])
            self._load_animation(self.current_animation)
            self._refresh_animation_list()
            self.animation_changed.emit()

    def _move_selected_left(self):
        """Move currently selected/playing frame left"""
        if not self.current_animation or self.current_playback_frame <= 0:
            return
        self._reorder_frames(self.current_playback_frame, self.current_playback_frame - 1)
        self.current_playback_frame -= 1
        self._update_current_frame_highlight()

    def _move_selected_right(self):
        """Move currently selected/playing frame right"""
        if not self.current_animation or self.current_playback_frame >= self.current_animation.frame_count - 1:
            return
        self._reorder_frames(self.current_playback_frame, self.current_playback_frame + 1)
        self.current_playback_frame += 1
        self._update_current_frame_highlight()

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

    def _on_color_override_changed(self, index):
        """Handle color override selection"""
        if index == 0:
            # "Original" selected
            self.current_color_override = None
        else:
            # Color index is index - 1 (accounting for "Original" at index 0)
            self.current_color_override = index - 1

        # Update preview to show the new color
        self._update_preview_display()

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
        self._update_preview()  # Show initial frame
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
        self.preview_widget.clear()

    def _rewind(self):
        """Rewind to start"""
        self.current_playback_frame = 0
        self._update_current_frame_highlight()
        self._update_playback_info()

    def _update_playback_timer(self):
        """Update timer interval based on current frame's duration and FPS"""
        if self.current_animation and self.current_playback_frame < self.current_animation.frame_count:
            frame = self.current_animation.get_frame(self.current_playback_frame)
            duration_frames = frame["duration"]
            # Calculate milliseconds: (duration in frames) / (frames per second) * 1000
            interval_ms = int((duration_frames / self.current_animation.fps) * 1000)
            self.playback_timer.setInterval(max(16, interval_ms))  # Minimum 16ms (~60fps max)

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
        self._update_preview()
        self._update_playback_timer()  # Update timer for next frame's duration

    def _update_current_frame_highlight(self):
        """Update which frame is highlighted as current"""
        for i, thumb in enumerate(self.frame_thumbnails):
            thumb.set_current(i == self.current_playback_frame)

    def _update_playback_info(self):
        """Update playback info label"""
        if self.current_animation:
            total_cards = self.current_animation.frame_count
            total_frames = self.current_animation.total_duration

            # Calculate current frame position (sum of durations before current card)
            current_frame = 0
            for i in range(self.current_playback_frame):
                card_data = self.current_animation.get_frame(i)
                current_frame += card_data["duration"]

            # Get current card duration for frame range display
            if self.current_playback_frame < total_cards:
                current_card = self.current_animation.get_frame(self.current_playback_frame)
                card_duration = current_card["duration"]
                frame_range = f"{current_frame + 1:03d}-{current_frame + card_duration:03d}"
            else:
                frame_range = f"{current_frame + 1:03d}"

            self.playback_info_label.setText(
                f"C: {self.current_playback_frame + 1:02d}/{total_cards:02d} | "
                f"F: {frame_range}/{total_frames:03d}"
            )
        else:
            self.playback_info_label.setText("C: 00/00 | F: 000/000")

    def _update_preview(self):
        """Update animation preview with current frame"""
        if self.current_animation and self.current_playback_frame < self.current_animation.frame_count:
            frame = self.current_animation.get_frame(self.current_playback_frame)
            self.preview_widget.set_card(frame["card_slot"], self.project, self.current_color_override)
        else:
            self.preview_widget.clear()

    def _update_preview_display(self):
        """Update preview display (for color override changes)"""
        # Re-render the current frame with the new color
        if self.is_playing:
            self._update_preview()
        else:
            # When not playing, just update the widget
            self.preview_widget.color_override = self.current_color_override
            self.preview_widget.update()
