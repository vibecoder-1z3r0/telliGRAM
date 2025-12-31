"""
Animation timeline editor widget.

Allows creating and editing GRAM card animation sequences.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QSpinBox, QLineEdit,
    QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QFont

from telligram.core.animation import Animation
from telligram.core.project import Project


class AnimationFrameItem(QWidget):
    """
    Widget representing a single frame in the timeline.

    Shows card slot number and duration.
    """

    def __init__(self, card_slot: int, duration: int, parent=None):
        super().__init__(parent)
        self.card_slot = card_slot
        self.duration = duration

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Card slot label
        slot_label = QLabel(f"Card {card_slot:02d}")
        slot_label.setStyleSheet("color: #cccccc; font-weight: bold;")
        layout.addWidget(slot_label)

        # Duration label
        duration_label = QLabel(f"× {duration}")
        duration_label.setStyleSheet("color: #888888;")
        layout.addWidget(duration_label)

        layout.addStretch()

        self.setStyleSheet("""
            AnimationFrameItem {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
                border-radius: 2px;
            }
        """)


class TimelineEditorWidget(QWidget):
    """
    Animation timeline editor.

    Create and edit animations by sequencing GRAM cards.
    """

    animation_changed = Signal()  # Emitted when animation is modified

    def __init__(self, project: Project = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_animation = None
        self.current_card_slot = 0  # Current card slot selected in main window
        self.is_playing = False
        self.play_frame = 0
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._advance_frame)

        self._create_ui()

    def _create_ui(self):
        """Create the UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # Title
        title = QLabel("Animation Timeline")
        title.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                font-weight: bold;
                padding: 4px;
            }
        """)
        main_layout.addWidget(title)

        # Animation selection group
        selection_group = QGroupBox("Animation")
        selection_layout = QHBoxLayout(selection_group)

        self.anim_list = QListWidget()
        self.anim_list.setMaximumHeight(100)
        self.anim_list.itemClicked.connect(self._on_animation_selected)
        selection_layout.addWidget(self.anim_list)

        button_layout = QVBoxLayout()
        self.new_anim_btn = QPushButton("New")
        self.new_anim_btn.clicked.connect(self._create_new_animation)
        button_layout.addWidget(self.new_anim_btn)

        self.delete_anim_btn = QPushButton("Delete")
        self.delete_anim_btn.clicked.connect(self._delete_animation)
        self.delete_anim_btn.setEnabled(False)
        button_layout.addWidget(self.delete_anim_btn)

        button_layout.addStretch()
        selection_layout.addLayout(button_layout)

        main_layout.addWidget(selection_group)

        # Animation properties
        props_group = QGroupBox("Properties")
        props_layout = QFormLayout(props_group)

        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_name_changed)
        props_layout.addRow("Name:", self.name_edit)

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(10)
        self.fps_spin.valueChanged.connect(self._on_fps_changed)
        props_layout.addRow("FPS:", self.fps_spin)

        main_layout.addWidget(props_group)

        # Frame list
        frames_group = QGroupBox("Frames")
        frames_layout = QVBoxLayout(frames_group)

        self.frame_list = QListWidget()
        self.frame_list.setMaximumHeight(150)
        self.frame_list.itemSelectionChanged.connect(self._on_frame_selected)
        frames_layout.addWidget(self.frame_list)

        # Frame controls
        frame_controls = QHBoxLayout()

        self.add_frame_btn = QPushButton("Add Frame")
        self.add_frame_btn.clicked.connect(self._add_current_card)
        self.add_frame_btn.setEnabled(False)
        frame_controls.addWidget(self.add_frame_btn)

        self.remove_frame_btn = QPushButton("Remove")
        self.remove_frame_btn.clicked.connect(self._remove_frame)
        self.remove_frame_btn.setEnabled(False)
        frame_controls.addWidget(self.remove_frame_btn)

        frame_controls.addStretch()

        # Frame duration
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setValue(2)
        self.duration_spin.setPrefix("Duration: ")
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        frame_controls.addWidget(self.duration_spin)

        frames_layout.addLayout(frame_controls)

        main_layout.addWidget(frames_group)

        # Playback controls
        playback_group = QGroupBox("Playback")
        playback_layout = QHBoxLayout(playback_group)

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self._toggle_playback)
        self.play_btn.setEnabled(False)
        playback_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self._stop_playback)
        self.stop_btn.setEnabled(False)
        playback_layout.addWidget(self.stop_btn)

        playback_layout.addStretch()

        self.playback_label = QLabel("Frame: 0 / 0")
        self.playback_label.setStyleSheet("color: #888888;")
        playback_layout.addWidget(self.playback_label)

        main_layout.addWidget(playback_group)

        main_layout.addStretch()

        # Apply dark theme
        self.setStyleSheet("""
            QGroupBox {
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #5c5c5c;
                padding: 4px 8px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
            }
            QListWidget {
                background-color: #2b2b2b;
                color: #cccccc;
                border: 1px solid #3c3c3c;
            }
            QLineEdit, QSpinBox {
                background-color: #2b2b2b;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                padding: 2px;
            }
        """)

    def set_project(self, project: Project):
        """Set the current project"""
        self.project = project
        self._refresh_animation_list()

    def set_current_card_slot(self, slot: int):
        """Update which card slot is currently selected"""
        self.current_card_slot = slot

    def _refresh_animation_list(self):
        """Refresh the list of animations"""
        self.anim_list.clear()
        if self.project:
            for anim in self.project.animations:
                item = QListWidgetItem(f"{anim.name} ({anim.frame_count} frames)")
                self.anim_list.addItem(item)

    def _create_new_animation(self):
        """Create a new animation"""
        if not self.project:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        # Create new animation with default name
        count = len(self.project.animations) + 1
        anim = Animation(name=f"Animation_{count}", fps=10)
        self.project.add_animation(anim)

        self._refresh_animation_list()
        self.animation_changed.emit()

        # Select the new animation
        self.anim_list.setCurrentRow(len(self.project.animations) - 1)
        self._on_animation_selected(self.anim_list.currentItem())

    def _delete_animation(self):
        """Delete selected animation"""
        if not self.current_animation or not self.project:
            return

        try:
            index = self.project.animations.index(self.current_animation)
            del self.project.animations[index]
            self.current_animation = None
            self._refresh_animation_list()
            self._update_ui_state()
            self.animation_changed.emit()
        except ValueError:
            pass

    def _on_animation_selected(self, item):
        """Handle animation selection"""
        if not item or not self.project:
            return

        index = self.anim_list.row(item)
        if 0 <= index < len(self.project.animations):
            self.current_animation = self.project.animations[index]
            self._load_animation_data()
            self._update_ui_state()

    def _load_animation_data(self):
        """Load current animation data into UI"""
        if not self.current_animation:
            return

        self.name_edit.setText(self.current_animation.name)
        self.fps_spin.setValue(self.current_animation.fps)
        self._refresh_frame_list()

    def _refresh_frame_list(self):
        """Refresh the frame list"""
        self.frame_list.clear()
        if not self.current_animation:
            return

        for i in range(self.current_animation.frame_count):
            frame = self.current_animation.get_frame(i)
            item = QListWidgetItem()
            widget = AnimationFrameItem(frame["card_slot"], frame["duration"])
            item.setSizeHint(widget.sizeHint())
            self.frame_list.addItem(item)
            self.frame_list.setItemWidget(item, widget)

    def _add_current_card(self):
        """Add current card slot to animation"""
        if not self.current_animation:
            return

        duration = self.duration_spin.value()
        self.current_animation.add_frame(self.current_card_slot, duration)
        self._refresh_frame_list()
        self._refresh_animation_list()
        self._update_ui_state()  # Enable play button if frames were added
        self.animation_changed.emit()

    def _remove_frame(self):
        """Remove selected frame"""
        if not self.current_animation:
            return

        current_row = self.frame_list.currentRow()
        if current_row >= 0:
            self.current_animation.remove_frame(current_row)
            self._refresh_frame_list()
            self._refresh_animation_list()
            self.animation_changed.emit()

    def _on_name_changed(self, text):
        """Handle animation name change"""
        if self.current_animation:
            self.current_animation.name = text
            self._refresh_animation_list()
            self.animation_changed.emit()

    def _on_fps_changed(self, value):
        """Handle FPS change"""
        if self.current_animation:
            self.current_animation.fps = value
            self.animation_changed.emit()

    def _on_frame_selected(self):
        """Handle frame selection in list"""
        if not self.current_animation:
            return

        current_row = self.frame_list.currentRow()
        if current_row >= 0 and current_row < self.current_animation.frame_count:
            frame = self.current_animation.get_frame(current_row)
            # Update duration spinner to show selected frame's duration
            self.duration_spin.blockSignals(True)  # Prevent triggering valueChanged
            self.duration_spin.setValue(frame["duration"])
            self.duration_spin.blockSignals(False)

    def _on_duration_changed(self, value):
        """Handle duration change for selected frame"""
        if not self.current_animation:
            return

        current_row = self.frame_list.currentRow()
        if current_row >= 0 and current_row < self.current_animation.frame_count:
            # Update the frame's duration
            frame = self.current_animation.get_frame(current_row)
            frame["duration"] = value
            self._refresh_frame_list()
            self._refresh_animation_list()
            self.animation_changed.emit()
            # Restore selection
            self.frame_list.setCurrentRow(current_row)

    def _update_ui_state(self):
        """Update UI button states"""
        has_animation = self.current_animation is not None
        has_frames = has_animation and self.current_animation.frame_count > 0

        self.delete_anim_btn.setEnabled(has_animation)
        self.add_frame_btn.setEnabled(has_animation)
        self.remove_frame_btn.setEnabled(has_frames)
        self.play_btn.setEnabled(has_frames)
        self.stop_btn.setEnabled(has_frames and self.is_playing)

    def _toggle_playback(self):
        """Toggle animation playback"""
        if not self.current_animation:
            return

        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        """Start playing animation"""
        if not self.current_animation or self.current_animation.frame_count == 0:
            return

        self.is_playing = True
        self.play_frame = 0
        self.play_btn.setText("⏸ Pause")
        self.stop_btn.setEnabled(True)

        # Calculate timer interval from FPS
        interval_ms = int(1000 / self.current_animation.fps)
        self.play_timer.start(interval_ms)

    def _pause_playback(self):
        """Pause animation playback"""
        self.is_playing = False
        self.play_timer.stop()
        self.play_btn.setText("▶ Play")

    def _stop_playback(self):
        """Stop animation playback"""
        self.is_playing = False
        self.play_timer.stop()
        self.play_frame = 0
        self.play_btn.setText("▶ Play")
        self.stop_btn.setEnabled(False)
        self.playback_label.setText("Frame: 0 / 0")

    def _advance_frame(self):
        """Advance to next frame in playback"""
        if not self.current_animation:
            return

        self.play_frame += 1

        # Loop back to start
        if self.play_frame >= self.current_animation.total_duration:
            self.play_frame = 0

        # Update label
        total = self.current_animation.total_duration
        self.playback_label.setText(f"Frame: {self.play_frame} / {total}")

        # TODO: Update pixel editor to show the current frame's card
        # This would require emitting a signal to the main window
