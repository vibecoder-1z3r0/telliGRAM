"""Enhanced timeline editor widget for animation sequences"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QSlider, QCheckBox, QSpinBox, QFrame, QComboBox,
    QLineEdit, QMessageBox, QInputDialog, QDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QMimeData, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QDrag

from telligram.core.project import Project
from telligram.core.animation import Animation, MAX_LAYERS
from telligram.core.constants import get_color_hex


class LayerEditorDialog(QDialog):
    """Dialog for editing layers in an animation frame"""

    def __init__(self, frame_index: int, animation: Animation, project: Project, parent=None):
        super().__init__(parent)
        self.frame_index = frame_index
        self.animation = animation
        self.project = project
        self.frame_data = animation.get_frame(frame_index)
        self.layers = self.frame_data.get("layers", []).copy()  # Work with a copy

        self.setWindowTitle(f"Edit Layers - Frame #{frame_index + 1}")
        self.setMinimumSize(400, 500)
        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(f"<h3>Frame #{self.frame_index + 1} Layers</h3>")
        layout.addWidget(header)

        info = QLabel(f"Manage up to {MAX_LAYERS} layers (0 = top priority)")
        info.setStyleSheet("color: #888;")
        layout.addWidget(info)

        # Layer list
        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.layer_list)

        # Layer controls
        controls = QHBoxLayout()

        self.add_btn = QPushButton("Add Layer")
        self.add_btn.clicked.connect(self._add_layer)
        controls.addWidget(self.add_btn)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self._remove_layer)
        controls.addWidget(self.remove_btn)

        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self._move_layer_up)
        controls.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self._move_layer_down)
        controls.addWidget(self.move_down_btn)

        self.toggle_vis_btn = QPushButton("Toggle Visibility")
        self.toggle_vis_btn.clicked.connect(self._toggle_visibility)
        controls.addWidget(self.toggle_vis_btn)

        self.duplicate_btn = QPushButton("Duplicate")
        self.duplicate_btn.clicked.connect(self._duplicate_layer)
        controls.addWidget(self.duplicate_btn)

        layout.addLayout(controls)

        # Dialog buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self._update_layer_list()

    def _update_layer_list(self):
        """Update the layer list display"""
        self.layer_list.clear()

        for i, layer in enumerate(self.layers):
            card_slot = layer.get("card_slot", 0)
            visible = layer.get("visible", True)
            vis_text = "👁" if visible else "🚫"
            item_text = f"Layer {i}: Slot {card_slot} {vis_text}"

            item = QListWidgetItem(item_text)
            self.layer_list.addItem(item)

        # Update button states
        has_selection = self.layer_list.currentRow() >= 0
        can_add = len(self.layers) < MAX_LAYERS

        self.add_btn.setEnabled(can_add)
        self.remove_btn.setEnabled(has_selection)
        self.move_up_btn.setEnabled(has_selection and self.layer_list.currentRow() > 0)
        self.move_down_btn.setEnabled(has_selection and self.layer_list.currentRow() < len(self.layers) - 1)
        self.toggle_vis_btn.setEnabled(has_selection)
        self.duplicate_btn.setEnabled(has_selection and can_add)

    def _add_layer(self):
        """Add a new layer"""
        if len(self.layers) >= MAX_LAYERS:
            return

        # Ask user for card slot
        card_slot, ok = QInputDialog.getInt(
            self,
            "Add Layer",
            "Enter card slot (0-63):",
            0, 0, 63
        )

        if ok:
            self.layers.append({"card_slot": card_slot, "visible": True})
            self._update_layer_list()

    def _remove_layer(self):
        """Remove selected layer"""
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.layers):
            self.layers.pop(row)
            self._update_layer_list()

    def _move_layer_up(self):
        """Move selected layer up (higher priority)"""
        row = self.layer_list.currentRow()
        if row > 0:
            self.layers[row], self.layers[row - 1] = self.layers[row - 1], self.layers[row]
            self._update_layer_list()
            self.layer_list.setCurrentRow(row - 1)

    def _move_layer_down(self):
        """Move selected layer down (lower priority)"""
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.layers) - 1:
            self.layers[row], self.layers[row + 1] = self.layers[row + 1], self.layers[row]
            self._update_layer_list()
            self.layer_list.setCurrentRow(row + 1)

    def _toggle_visibility(self):
        """Toggle visibility of selected layer"""
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.layers):
            self.layers[row]["visible"] = not self.layers[row].get("visible", True)
            self._update_layer_list()
            self.layer_list.setCurrentRow(row)

    def _duplicate_layer(self):
        """Duplicate selected layer"""
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.layers) and len(self.layers) < MAX_LAYERS:
            new_layer = self.layers[row].copy()
            self.layers.insert(row + 1, new_layer)
            self._update_layer_list()
            self.layer_list.setCurrentRow(row + 1)

    def get_layers(self):
        """Get the modified layers list"""
        return self.layers


class FrameThumbnail(QFrame):
    """Visual thumbnail for a single frame in the timeline"""

    clicked = Signal(int)  # Emits frame index when clicked
    duration_changed = Signal(int, int)  # Emits (frame_index, new_duration)
    remove_requested = Signal(int)  # Emits frame index to remove
    reorder_requested = Signal(int, int)  # Emits (from_index, to_index)
    duplicate_requested = Signal(int)  # Emits frame index to duplicate
    edit_layers_requested = Signal(int)  # Emits frame index to edit layers

    def __init__(self, frame_index: int):
        super().__init__()
        self.frame_index = frame_index
        self.layers = []  # List of {"card_slot": int, "visible": bool}
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

    def set_frame_data(self, layers: list, duration: int, project: Project):
        """
        Set frame data with layers.

        Args:
            layers: List of layer dicts with 'card_slot' and 'visible' keys
            duration: Frame duration
            project: Project reference
        """
        self.layers = layers if layers else []
        self.project = project
        self.duration_spin.setValue(duration)

        # Update label to show layer count
        visible_count = sum(1 for layer in self.layers if layer.get("visible", True))
        if len(self.layers) == 0:
            self.slot_label.setText("No layers")
        elif len(self.layers) == 1:
            self.slot_label.setText(f"Slot {self.layers[0]['card_slot']}")
        else:
            self.slot_label.setText(f"{visible_count}/{len(self.layers)} layers")

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

        duplicate_action = QAction("Duplicate Frame", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_requested.emit(self.frame_index))
        menu.addAction(duplicate_action)

        menu.addSeparator()

        edit_layers_action = QAction("Edit Layers...", self)
        edit_layers_action.triggered.connect(self._edit_layers)
        menu.addAction(edit_layers_action)

        menu.addSeparator()

        remove_action = QAction("Remove Frame", self)
        remove_action.triggered.connect(lambda: self.remove_requested.emit(self.frame_index))
        menu.addAction(remove_action)

        menu.exec(event.globalPos())

    def _edit_layers(self):
        """Emit signal to edit layers"""
        self.edit_layers_requested.emit(self.frame_index)

    def paintEvent(self, event):
        """Paint layered card preview"""
        super().paintEvent(event)

        if self.project is None:
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

        # Draw layers from bottom to top (reverse order, since index 0 = top priority)
        for layer in reversed(self.layers):
            if not layer.get("visible", True):
                continue  # Skip invisible layers

            card_slot = layer.get("card_slot")
            if card_slot is None:
                continue

            card = self.project.get_card(card_slot)
            if card is None:
                continue

            # Get card color
            card_color = get_color_hex(card.color) if hasattr(card, 'color') else "#FFFFFF"

            # Draw pixels (only non-transparent pixels)
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

        # Draw grid on top
        painter.setPen(QPen(QColor("#333"), 1))
        for i in range(9):
            # Vertical lines
            x = preview_x + i * pixel_size
            painter.drawLine(x, preview_y, x, preview_y + preview_size)
            # Horizontal lines
            y = preview_y + i * pixel_size
            painter.drawLine(preview_x, y, preview_x + preview_size, y)


class AnimationPreviewWidget(QFrame):
    """Preview widget showing the current animation frame with layer compositing"""

    def __init__(self):
        super().__init__()
        self.project = None
        self.current_layers = []
        self.setFixedSize(200, 200)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background-color: #1a1a1a; border: 2px solid #3c3c3c;")

    def set_layers(self, layers: list, project):
        """Set the layers to display"""
        self.current_layers = layers if layers else []
        self.project = project
        self.update()

    def clear(self):
        """Clear the preview"""
        self.current_layers = []
        self.update()

    def paintEvent(self, event):
        """Paint the layered card preview"""
        super().paintEvent(event)

        painter = QPainter(self)

        if self.project is None or len(self.current_layers) == 0:
            # Draw "no animation" text
            painter.setPen(QColor("#888"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No Preview")
            return

        # Draw card preview (160x160 centered)
        preview_size = 160
        pixel_size = preview_size // 8
        offset_x = (200 - preview_size) // 2
        offset_y = (200 - preview_size) // 2

        # Draw background
        painter.fillRect(offset_x, offset_y, preview_size, preview_size, QColor("#1a1a1a"))

        # Draw layers from bottom to top (reverse order, since index 0 = top priority)
        for layer in reversed(self.current_layers):
            if not layer.get("visible", True):
                continue  # Skip invisible layers

            card_slot = layer.get("card_slot")
            if card_slot is None:
                continue

            card = self.project.get_card(card_slot)
            if card is None:
                continue

            # Get card color
            card_color = get_color_hex(card.color) if hasattr(card, 'color') else "#FFFFFF"

            # Draw pixels (only non-transparent pixels)
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

        self.add_frame_btn = QPushButton("Add Current Card")
        self.add_frame_btn.clicked.connect(self._add_current_card)
        frame_controls.addWidget(self.add_frame_btn)

        self.insert_frame_btn = QPushButton("Insert Before Selected")
        self.insert_frame_btn.clicked.connect(self._insert_frame)
        frame_controls.addWidget(self.insert_frame_btn)

        frame_controls.addWidget(QLabel("|"))

        self.move_left_btn = QPushButton("◀ Move Left")
        self.move_left_btn.clicked.connect(self._move_selected_left)
        frame_controls.addWidget(self.move_left_btn)

        self.move_right_btn = QPushButton("Move Right ▶")
        self.move_right_btn.clicked.connect(self._move_selected_right)
        frame_controls.addWidget(self.move_right_btn)

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
        if len(project.animations) > 0:
            self.animation_combo.setCurrentIndex(0)
            # Manually load the first animation since signals are blocked during refresh
            self._load_animation(project.animations[0])
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
        # Use layers from frame data
        layers = frame_data.get("layers", [])
        thumb.set_frame_data(layers, frame_data["duration"], self.project)
        thumb.clicked.connect(self._on_frame_clicked)
        thumb.duration_changed.connect(self._on_frame_duration_changed)
        thumb.remove_requested.connect(self._remove_frame_at)
        thumb.reorder_requested.connect(self._reorder_frames)
        thumb.duplicate_requested.connect(self._duplicate_frame)
        thumb.edit_layers_requested.connect(self._edit_frame_layers)

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

    def _edit_frame_layers(self, frame_index: int):
        """Open layer editor dialog for a frame"""
        if not self.current_animation or frame_index >= self.current_animation.frame_count:
            return

        if not self.project:
            return

        # Open layer editor dialog
        dialog = LayerEditorDialog(frame_index, self.current_animation, self.project, self)

        if dialog.exec() == QDialog.Accepted:
            # Get modified layers
            new_layers = dialog.get_layers()

            # Update the frame's layers
            frame = self.current_animation.get_frame(frame_index)
            old_layers = frame.get("layers", []).copy()

            # Only update if changed
            if new_layers != old_layers:
                frame["layers"] = new_layers
                # Reload animation to refresh UI
                self._load_animation(self.current_animation)
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
            total = self.current_animation.frame_count
            self.playback_info_label.setText(f"Frame: {self.current_playback_frame + 1} / {total}")
        else:
            self.playback_info_label.setText("Frame: 0 / 0")

    def _update_preview(self):
        """Update animation preview with current frame"""
        if self.current_animation and self.current_playback_frame < self.current_animation.frame_count:
            frame = self.current_animation.get_frame(self.current_playback_frame)
            layers = frame.get("layers", [])
            self.preview_widget.set_layers(layers, self.project)
        else:
            self.preview_widget.clear()
