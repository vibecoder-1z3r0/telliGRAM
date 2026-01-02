"""
Composite preview widget for layered animation compositing.

Allows users to combine multiple animations as layers with individual
controls for visibility, color override, and end behavior.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSlider, QFrame, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor

from telligram.core.project import Project
from telligram.core.composite import LayerComposite
from telligram.core.constants import get_color_hex, COLOR_NAMES


class LayerControlWidget(QFrame):
    """
    Controls for a single layer in the composite.

    Includes checkbox, animation selector, color override, and end behavior.
    """

    layer_changed = Signal()  # Emitted when any layer setting changes

    def __init__(self, layer_index: int, project: Project):
        super().__init__()
        self.layer_index = layer_index
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Top row: checkbox and animation selector
        top_layout = QHBoxLayout()

        self.visible_check = QCheckBox(f"Layer {layer_index + 1}")
        self.visible_check.setChecked(False)
        self.visible_check.stateChanged.connect(lambda: self.layer_changed.emit())
        top_layout.addWidget(self.visible_check)

        self.animation_combo = QComboBox()
        self.animation_combo.setEnabled(False)
        self.animation_combo.currentIndexChanged.connect(self._on_animation_changed)
        top_layout.addWidget(self.animation_combo, 1)

        layout.addLayout(top_layout)

        # Bottom row: color override and end behavior
        bottom_layout = QHBoxLayout()

        bottom_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItem("Original", None)
        for i, color_name in enumerate(COLOR_NAMES):
            self.color_combo.addItem(color_name, i)
        self.color_combo.setEnabled(False)
        self.color_combo.currentIndexChanged.connect(lambda: self.layer_changed.emit())
        bottom_layout.addWidget(self.color_combo)

        bottom_layout.addWidget(QLabel("When ends:"))
        self.end_behavior_combo = QComboBox()
        self.end_behavior_combo.addItem("Loop", "loop")
        self.end_behavior_combo.addItem("Hold", "hold")
        self.end_behavior_combo.addItem("Hide", "hide")
        self.end_behavior_combo.setEnabled(False)
        self.end_behavior_combo.currentIndexChanged.connect(lambda: self.layer_changed.emit())
        bottom_layout.addWidget(self.end_behavior_combo)

        layout.addLayout(bottom_layout)

        # Connect visible checkbox to enable/disable controls
        self.visible_check.stateChanged.connect(self._on_visible_changed)

    def _on_visible_changed(self, state):
        """Enable/disable controls based on checkbox"""
        enabled = state == Qt.CheckState.Checked
        self.animation_combo.setEnabled(enabled)
        self.color_combo.setEnabled(enabled)
        self.end_behavior_combo.setEnabled(enabled)

    def _on_animation_changed(self):
        """Handle animation selection change"""
        self.layer_changed.emit()

    def update_animations(self, project: Project):
        """Update animation dropdown with current project animations"""
        self.project = project
        current = self.animation_combo.currentText()

        self.animation_combo.clear()
        for anim in project.animations:
            self.animation_combo.addItem(anim.name)

        # Restore previous selection if possible
        index = self.animation_combo.findText(current)
        if index >= 0:
            self.animation_combo.setCurrentIndex(index)

    def get_layer_config(self) -> dict:
        """Get current layer configuration"""
        if not self.visible_check.isChecked():
            return None

        if self.animation_combo.currentIndex() < 0:
            return None

        return {
            "animation_name": self.animation_combo.currentText(),
            "visible": True,
            "end_behavior": self.end_behavior_combo.currentData(),
            "color_override": self.color_combo.currentData()
        }

    def set_layer_config(self, config: dict):
        """Set layer configuration"""
        if config is None:
            self.visible_check.setChecked(False)
            return

        self.visible_check.setChecked(config.get("visible", True))

        # Set animation
        anim_name = config.get("animation_name", "")
        index = self.animation_combo.findText(anim_name)
        if index >= 0:
            self.animation_combo.setCurrentIndex(index)

        # Set color override
        color_override = config.get("color_override")
        if color_override is None:
            self.color_combo.setCurrentIndex(0)  # Original
        else:
            index = self.color_combo.findData(color_override)
            if index >= 0:
                self.color_combo.setCurrentIndex(index)

        # Set end behavior
        end_behavior = config.get("end_behavior", "loop")
        index = self.end_behavior_combo.findData(end_behavior)
        if index >= 0:
            self.end_behavior_combo.setCurrentIndex(index)


class CompositePreviewArea(QWidget):
    """
    Preview area showing the composited animation result.

    Renders all visible layers composited together.
    """

    def __init__(self):
        super().__init__()
        self.project = None
        self.composite = None
        self.current_frame = 0
        self.pixel_size = 30

        # Calculate size (8x8 grid)
        total_size = self.pixel_size * 8
        self.setFixedSize(total_size, total_size)

    def set_composite(self, composite: LayerComposite, project: Project):
        """Set composite to preview"""
        self.composite = composite
        self.project = project
        self.update()

    def set_frame(self, frame_num: int):
        """Set current frame to display"""
        self.current_frame = frame_num
        self.update()

    def clear(self):
        """Clear preview"""
        self.composite = None
        self.project = None
        self.update()

    def paintEvent(self, event):
        """Draw the composited frame"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(40, 40, 40))

        if not self.composite or not self.project:
            return

        # Get card slots for all layers at current frame
        card_slots = self.composite.get_card_at_frame(self.current_frame, self.project)

        # Draw layers from bottom to top (reverse order for proper layering)
        for layer_idx in reversed(range(8)):
            card_slot = card_slots[layer_idx]
            if card_slot is None:
                continue

            card = self.project.get_card(card_slot)
            if card is None:
                continue

            # Determine color to use
            layer_config = self.composite.layers[layer_idx] if layer_idx < len(self.composite.layers) else None
            if layer_config and layer_config.get("color_override") is not None:
                color_index = layer_config["color_override"]
            else:
                color_index = card.color

            color = QColor(get_color_hex(color_index))

            # Draw each pixel
            for y in range(8):
                for x in range(8):
                    if card.get_pixel(x, y):
                        painter.fillRect(
                            x * self.pixel_size,
                            y * self.pixel_size,
                            self.pixel_size,
                            self.pixel_size,
                            color
                        )


class CompositePreviewWidget(QWidget):
    """
    Complete composite preview widget.

    Includes composite selector, layer controls, playback controls,
    and preview area.
    """

    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        self.current_composite = None
        self.is_playing = False
        self.current_frame = 0

        self.layer_controls = []

        self.setup_ui()

        # Playback timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._advance_frame)

    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)

        # Composite selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Composite:"))

        self.composite_combo = QComboBox()
        self.composite_combo.currentIndexChanged.connect(self._on_composite_selected)
        selector_layout.addWidget(self.composite_combo, 1)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_composite)
        selector_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_composite)
        selector_layout.addWidget(self.delete_btn)

        layout.addLayout(selector_layout)

        # Layer controls in scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.StyledPanel)

        layer_container = QWidget()
        layer_layout = QVBoxLayout(layer_container)

        layer_layout.addWidget(QLabel("Layers to composite:"))

        # Create 8 layer controls
        for i in range(8):
            layer_control = LayerControlWidget(i, self.project)
            layer_control.layer_changed.connect(self._on_layer_changed)
            self.layer_controls.append(layer_control)
            layer_layout.addWidget(layer_control)

        layer_layout.addStretch()
        scroll.setWidget(layer_container)
        layout.addWidget(scroll, 1)

        # Playback controls
        playback_group = QGroupBox("Playback")
        playback_layout = QVBoxLayout(playback_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self._toggle_playback)
        btn_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self._stop_playback)
        btn_layout.addWidget(self.stop_btn)

        self.rewind_btn = QPushButton("⏮ Rewind")
        self.rewind_btn.clicked.connect(self._rewind)
        btn_layout.addWidget(self.rewind_btn)

        playback_layout.addLayout(btn_layout)

        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(120)
        self.speed_slider.setValue(60)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel("60 fps")
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(f"{v} fps")
        )
        speed_layout.addWidget(self.speed_label)
        playback_layout.addLayout(speed_layout)

        # Loop checkbox
        self.loop_check = QCheckBox("Loop")
        self.loop_check.setChecked(False)
        playback_layout.addWidget(self.loop_check)

        layout.addWidget(playback_group)

        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setAlignment(Qt.AlignCenter)

        self.preview_area = CompositePreviewArea()
        preview_layout.addWidget(self.preview_area, alignment=Qt.AlignCenter)

        layout.addWidget(preview_group)

        # Update composite list
        self.refresh_composite_list()

    def refresh_composite_list(self):
        """Refresh composite selector dropdown"""
        current = self.composite_combo.currentText()

        self.composite_combo.clear()
        self.composite_combo.addItem("(new)", None)

        for comp in self.project.composites:
            self.composite_combo.addItem(comp.name, comp)

        # Restore selection
        index = self.composite_combo.findText(current)
        if index >= 0:
            self.composite_combo.setCurrentIndex(index)

    def update_animations(self):
        """Update all layer controls with current animations"""
        for layer_control in self.layer_controls:
            layer_control.update_animations(self.project)

    def _on_composite_selected(self, index):
        """Handle composite selection"""
        composite = self.composite_combo.currentData()

        if composite is None:
            # New composite
            self.current_composite = LayerComposite("New Composite")
            self._clear_layer_controls()
        else:
            # Load existing composite
            self.current_composite = composite
            self._load_composite_to_controls()

        self._update_preview()

    def _clear_layer_controls(self):
        """Clear all layer controls"""
        for layer_control in self.layer_controls:
            layer_control.set_layer_config(None)

    def _load_composite_to_controls(self):
        """Load current composite into layer controls"""
        if not self.current_composite:
            return

        # Update playback settings
        self.speed_slider.setValue(self.current_composite.fps)
        self.loop_check.setChecked(self.current_composite.loop)

        # Load layers
        for i in range(8):
            if i < len(self.current_composite.layers):
                self.layer_controls[i].set_layer_config(self.current_composite.layers[i])
            else:
                self.layer_controls[i].set_layer_config(None)

    def _on_layer_changed(self):
        """Handle layer control change"""
        self._update_composite_from_controls()
        self._update_preview()

    def _update_composite_from_controls(self):
        """Update current composite from layer controls"""
        if not self.current_composite:
            return

        # Clear and rebuild layers
        self.current_composite.layers.clear()

        for layer_control in self.layer_controls:
            config = layer_control.get_layer_config()
            if config:
                self.current_composite.layers.append(config)
            else:
                # Add placeholder for empty layer
                self.current_composite.layers.append({
                    "animation_name": "",
                    "visible": False,
                    "end_behavior": "loop",
                    "color_override": None
                })

        # Update playback settings
        self.current_composite.fps = self.speed_slider.value()
        self.current_composite.loop = self.loop_check.isChecked()

    def _update_preview(self):
        """Update preview area"""
        if self.current_composite:
            self.preview_area.set_composite(self.current_composite, self.project)
            self.preview_area.set_frame(self.current_frame)
        else:
            self.preview_area.clear()

    def _save_composite(self):
        """Save current composite to project"""
        # TODO: Show dialog to get name
        # For now, just add/update composite
        if self.current_composite:
            # Check if already exists
            existing = self.project.get_composite(self.current_composite.name)
            if existing:
                # Update existing
                existing.layers = self.current_composite.layers.copy()
                existing.fps = self.current_composite.fps
                existing.loop = self.current_composite.loop
            else:
                # Add new
                self.project.add_composite(self.current_composite)

            self.refresh_composite_list()

    def _delete_composite(self):
        """Delete current composite"""
        composite = self.composite_combo.currentData()
        if composite and composite in self.project.composites:
            self.project.composites.remove(composite)
            self.refresh_composite_list()

    def _toggle_playback(self):
        """Toggle play/pause"""
        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        """Start playback"""
        if not self.current_composite:
            return

        self.is_playing = True
        self.play_btn.setText("⏸ Pause")

        # Calculate interval from fps
        fps = self.speed_slider.value()
        interval = int(1000 / fps)  # milliseconds
        self.timer.start(interval)

    def _pause_playback(self):
        """Pause playback"""
        self.is_playing = False
        self.play_btn.setText("▶ Play")
        self.timer.stop()

    def _stop_playback(self):
        """Stop playback and rewind"""
        self._pause_playback()
        self._rewind()

    def _rewind(self):
        """Rewind to start"""
        self.current_frame = 0
        self._update_preview()

    def _advance_frame(self):
        """Advance to next frame"""
        if not self.current_composite:
            return

        max_duration = self.current_composite.get_max_duration(self.project)

        self.current_frame += 1

        if self.current_frame >= max_duration:
            if self.loop_check.isChecked():
                self.current_frame = 0
            else:
                self._stop_playback()
                return

        self._update_preview()
