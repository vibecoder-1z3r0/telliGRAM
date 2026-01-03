"""
Composite preview widget for layered animation compositing.

Allows users to combine multiple animations as layers with individual
controls for visibility, color override, and end behavior.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSlider, QFrame, QGroupBox, QScrollArea,
    QInputDialog, QMessageBox, QSpinBox
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
    move_up_requested = Signal(int)  # Emitted when move up clicked (layer_index)
    move_down_requested = Signal(int)  # Emitted when move down clicked (layer_index)

    def __init__(self, layer_index: int, project: Project):
        super().__init__()
        self.layer_index = layer_index
        self.project = project

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Top row: checkbox, animation selector, and move buttons
        top_layout = QHBoxLayout()

        # Name the first layer "Parent/Base Layer", others "Layer 1" through "Layer 7"
        if layer_index == 0:
            layer_name = "Parent/Base Layer"
        else:
            layer_name = f"Layer {layer_index}"

        self.visible_check = QCheckBox(layer_name)
        self.visible_check.setChecked(False)
        self.visible_check.stateChanged.connect(lambda: self.layer_changed.emit())
        top_layout.addWidget(self.visible_check)

        # Add move up/down buttons
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.setMaximumWidth(30)
        self.move_up_btn.setToolTip("Move layer up")
        self.move_up_btn.clicked.connect(lambda: self.move_up_requested.emit(self.layer_index))
        top_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.setMaximumWidth(30)
        self.move_down_btn.setToolTip("Move layer down")
        self.move_down_btn.clicked.connect(lambda: self.move_down_requested.emit(self.layer_index))
        top_layout.addWidget(self.move_down_btn)

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

        # Offset row: X and Y offsets
        offset_layout = QHBoxLayout()

        offset_layout.addWidget(QLabel("X Offset:"))
        self.x_offset_spin = QSpinBox()
        self.x_offset_spin.setRange(-8, 8)  # One card width in either direction
        self.x_offset_spin.setValue(0)
        self.x_offset_spin.setEnabled(False)
        self.x_offset_spin.valueChanged.connect(lambda: self.layer_changed.emit())
        offset_layout.addWidget(self.x_offset_spin)

        offset_layout.addWidget(QLabel("Y Offset:"))
        self.y_offset_spin = QSpinBox()
        self.y_offset_spin.setRange(-8, 8)  # One card height in either direction
        self.y_offset_spin.setValue(0)
        self.y_offset_spin.setEnabled(False)
        self.y_offset_spin.valueChanged.connect(lambda: self.layer_changed.emit())
        offset_layout.addWidget(self.y_offset_spin)

        layout.addLayout(offset_layout)

        # Stack/Stitch row (only for layers 1-7, not Parent/Base)
        if layer_index > 0:
            stack_stitch_layout = QHBoxLayout()
            stack_stitch_layout.addWidget(QLabel("Position:"))

            self.stack_stitch_combo = QComboBox()
            self.stack_stitch_combo.addItem("Independent", "none")
            self.stack_stitch_combo.addItem("Stack Below", "stack")
            self.stack_stitch_combo.addItem("Stitch Below", "stitch")
            self.stack_stitch_combo.setEnabled(False)
            self.stack_stitch_combo.currentIndexChanged.connect(lambda: self.layer_changed.emit())
            stack_stitch_layout.addWidget(self.stack_stitch_combo)
            stack_stitch_layout.addStretch()

            layout.addLayout(stack_stitch_layout)
        else:
            # Parent/Base layer doesn't have stack/stitch option
            self.stack_stitch_combo = None

        # Connect visible checkbox to enable/disable controls
        self.visible_check.stateChanged.connect(self._on_visible_changed)

    def _on_visible_changed(self, state):
        """Enable/disable controls based on checkbox"""
        enabled = state == Qt.CheckState.Checked
        self.animation_combo.setEnabled(enabled)
        self.color_combo.setEnabled(enabled)
        self.end_behavior_combo.setEnabled(enabled)
        self.x_offset_spin.setEnabled(enabled)
        self.y_offset_spin.setEnabled(enabled)
        if self.stack_stitch_combo:
            self.stack_stitch_combo.setEnabled(enabled)

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
        is_visible = self.visible_check.isChecked()

        # Always return a config dict to preserve settings even when layer is unchecked
        config = {
            "animation_name": self.animation_combo.currentText() if self.animation_combo.currentIndex() >= 0 else "",
            "visible": is_visible,
            "end_behavior": self.end_behavior_combo.currentData(),
            "color_override": self.color_combo.currentData(),
            "x_offset": self.x_offset_spin.value(),
            "y_offset": self.y_offset_spin.value()
        }

        # Add stack_stitch mode if available (layers 1-7)
        if self.stack_stitch_combo:
            config["stack_stitch"] = self.stack_stitch_combo.currentData()
        else:
            config["stack_stitch"] = "none"

        return config

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

        # Set offsets
        self.x_offset_spin.setValue(config.get("x_offset", 0))
        self.y_offset_spin.setValue(config.get("y_offset", 0))

        # Set stack/stitch mode if available
        if self.stack_stitch_combo:
            stack_stitch = config.get("stack_stitch", "none")
            index = self.stack_stitch_combo.findData(stack_stitch)
            if index >= 0:
                self.stack_stitch_combo.setCurrentIndex(index)


class CompositePreviewArea(QWidget):
    """
    Preview area showing the composited animation result.

    Renders all visible layers composited together.
    Displays 32x32 card pixels (4x4 cards) to accommodate stacking/stitching/offsets.
    """

    def __init__(self):
        super().__init__()
        self.project = None
        self.composite = None
        self.current_frame = 0
        self.pixel_size = 8  # Smaller pixels to fit 32x32 in same space
        self.show_grid = True  # Grid enabled by default

        # Calculate size (32x32 grid = 4 cards x 4 cards)
        # 8 * 32 = 256x256 (close to original 240x240)
        total_size = self.pixel_size * 32
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
        from PySide6.QtGui import QPen

        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(40, 40, 40))

        # Center the 8x8 sprite in the 32x32 space (offset by 12 card pixels)
        offset_x = 12 * self.pixel_size
        offset_y = 12 * self.pixel_size

        if self.composite and self.project:
            # Get card slots for all layers at current frame
            card_slots = self.composite.get_card_at_frame(self.current_frame, self.project)

            # Calculate cumulative stack/stitch positions for each layer
            # Each layer's base position is determined by stack/stitch relative to layer below
            layer_positions = {}  # layer_idx -> (base_x_cards, base_y_cards)

            for layer_idx in range(8):
                layer_config = self.composite.layers[layer_idx] if layer_idx < len(self.composite.layers) else None

                if layer_idx == 0:
                    # Parent/Base layer starts at origin
                    layer_positions[layer_idx] = (0, 0)
                else:
                    # Check if this layer is stacked/stitched to layer below
                    stack_stitch = layer_config.get("stack_stitch", "none") if layer_config else "none"

                    # Get position of layer below
                    prev_x, prev_y = layer_positions.get(layer_idx - 1, (0, 0))

                    if stack_stitch == "stack":
                        # Stack below: same X, Y + 8
                        layer_positions[layer_idx] = (prev_x, prev_y + 8)
                    elif stack_stitch == "stitch":
                        # Stitch to right: X + 8, same Y
                        layer_positions[layer_idx] = (prev_x + 8, prev_y)
                    else:
                        # Independent: starts at origin
                        layer_positions[layer_idx] = (0, 0)

            # Draw layers from bottom to top (Parent/Base first, then Layer 1, 2, etc.)
            for layer_idx in range(8):
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

                # Get base position from stack/stitch
                base_x_cards, base_y_cards = layer_positions.get(layer_idx, (0, 0))

                # Get additional offsets
                x_offset_cards = layer_config.get("x_offset", 0) if layer_config else 0
                y_offset_cards = layer_config.get("y_offset", 0) if layer_config else 0

                # Draw each pixel (centered in preview + stack/stitch position + layer offset)
                for y in range(8):
                    for x in range(8):
                        if card.get_pixel(x, y):
                            # Apply all offsets in card pixels
                            final_x = offset_x + (base_x_cards + x + x_offset_cards) * self.pixel_size
                            final_y = offset_y + (base_y_cards + y + y_offset_cards) * self.pixel_size
                            painter.fillRect(
                                final_x,
                                final_y,
                                self.pixel_size,
                                self.pixel_size,
                                color
                            )

        # Draw grid if enabled
        if self.show_grid:
            painter.setPen(QPen(QColor(60, 60, 60), 1))
            # Draw 32x32 grid
            for i in range(33):
                # Vertical lines
                x = i * self.pixel_size
                painter.drawLine(x, 0, x, 32 * self.pixel_size)
                # Horizontal lines
                y = i * self.pixel_size
                painter.drawLine(0, y, 32 * self.pixel_size, y)


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

        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self._new_composite)
        selector_layout.addWidget(self.new_btn)

        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self._rename_composite)
        selector_layout.addWidget(self.rename_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_composite)
        selector_layout.addWidget(self.delete_btn)

        layout.addLayout(selector_layout)

        # Layer controls in scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.StyledPanel)

        layer_container = QWidget()
        self.layer_layout = QVBoxLayout(layer_container)

        # Header with layer management buttons
        layer_header_layout = QHBoxLayout()
        layer_header_layout.addWidget(QLabel("Layers to composite:"))
        layer_header_layout.addStretch()

        self.add_layer_btn = QPushButton("Add Layer")
        self.add_layer_btn.clicked.connect(self._add_layer)
        layer_header_layout.addWidget(self.add_layer_btn)

        self.remove_layer_btn = QPushButton("Remove Layer")
        self.remove_layer_btn.clicked.connect(self._remove_layer)
        self.remove_layer_btn.setEnabled(False)  # Start with only 2 layers
        layer_header_layout.addWidget(self.remove_layer_btn)

        self.layer_layout.addLayout(layer_header_layout)

        # Create 8 layer controls (initially hidden except first 2)
        for i in range(8):
            layer_control = LayerControlWidget(i, self.project)
            layer_control.layer_changed.connect(self._on_layer_changed)
            layer_control.move_up_requested.connect(self._move_layer_up)
            layer_control.move_down_requested.connect(self._move_layer_down)
            self.layer_controls.append(layer_control)
            self.layer_layout.addWidget(layer_control)
            # Hide layers 2-7 initially (only show Parent/Base + Layer 1)
            if i >= 2:
                layer_control.hide()

        self.layer_layout.addStretch()
        scroll.setWidget(layer_container)
        layout.addWidget(scroll, 1)

        # Track number of visible layers (start with 2: Parent/Base + Layer 1)
        self.num_visible_layers = 2
        self._update_layer_buttons()

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
        self.speed_slider.setMaximum(60)  # Cap at 60 FPS (Intellivision's refresh rate)
        self.speed_slider.setValue(60)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel("60 fps")
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        speed_layout.addWidget(self.speed_label)
        playback_layout.addLayout(speed_layout)

        # Loop checkbox
        self.loop_check = QCheckBox("Loop")
        self.loop_check.setChecked(False)
        playback_layout.addWidget(self.loop_check)

        # Grid checkbox
        self.grid_check = QCheckBox("Grid")
        self.grid_check.setChecked(True)
        self.grid_check.stateChanged.connect(self._on_grid_changed)
        playback_layout.addWidget(self.grid_check)

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

        for comp in self.project.composites:
            self.composite_combo.addItem(comp.name, comp)

        # Restore selection or select first if available
        index = self.composite_combo.findText(current)
        if index >= 0:
            self.composite_combo.setCurrentIndex(index)
        elif self.composite_combo.count() > 0:
            self.composite_combo.setCurrentIndex(0)

        # Enable/disable buttons based on selection
        has_composite = self.composite_combo.count() > 0
        self.rename_btn.setEnabled(has_composite)
        self.delete_btn.setEnabled(has_composite)

    def update_animations(self):
        """Update all layer controls with current animations"""
        for layer_control in self.layer_controls:
            layer_control.update_animations(self.project)

    def _on_composite_selected(self, index):
        """Handle composite selection"""
        composite = self.composite_combo.currentData()

        if composite:
            # Load existing composite
            self.current_composite = composite
            self._load_composite_to_controls()
            self._update_preview()
        else:
            # No composite selected
            self.current_composite = None
            self._clear_layer_controls()
            self._update_preview()

    def _clear_layer_controls(self):
        """Clear all layer controls"""
        for layer_control in self.layer_controls:
            layer_control.set_layer_config(None)

    def _load_composite_to_controls(self):
        """Load current composite into layer controls"""
        if not self.current_composite:
            return

        # Block signals while loading to prevent premature updates
        for layer_control in self.layer_controls:
            layer_control.blockSignals(True)

        # Update playback settings
        self.speed_slider.setValue(self.current_composite.fps)
        self.loop_check.setChecked(self.current_composite.loop)

        # Count how many layers are actually configured (visible or with animation)
        num_configured_layers = 0
        for i, layer_config in enumerate(self.current_composite.layers):
            if layer_config.get("visible") or layer_config.get("animation_name"):
                num_configured_layers = i + 1

        # Ensure at least 2 layers are visible (Parent/Base + Layer 1)
        num_layers_to_show = max(2, num_configured_layers)

        # Show/hide layer controls as needed
        for i in range(8):
            if i < num_layers_to_show:
                self.layer_controls[i].show()
            else:
                self.layer_controls[i].hide()

        self.num_visible_layers = num_layers_to_show
        self._update_layer_buttons()

        # Load layer configurations
        for i in range(8):
            if i < len(self.current_composite.layers):
                self.layer_controls[i].set_layer_config(self.current_composite.layers[i])
            else:
                self.layer_controls[i].set_layer_config(None)

        # Unblock signals after all configs are loaded
        for layer_control in self.layer_controls:
            layer_control.blockSignals(False)

        # Update stack/stitch states to prevent chaining
        self._update_stack_stitch_states()

    def _on_layer_changed(self):
        """Handle layer control change"""
        self._update_composite_from_controls()
        self._update_preview()
        self._update_stack_stitch_states()

    def _update_stack_stitch_states(self):
        """Update stack/stitch dropdown states to prevent chaining"""
        for i in range(1, 8):  # Layers 1-7 (not Parent/Base)
            layer_control = self.layer_controls[i]

            # Skip if this layer doesn't have stack/stitch combo (shouldn't happen for i > 0)
            if not layer_control.stack_stitch_combo:
                continue

            # Check if previous layer is stacked or stitched
            prev_layer_control = self.layer_controls[i - 1]
            prev_config = prev_layer_control.get_layer_config()

            if prev_config:
                prev_stack_stitch = prev_config.get("stack_stitch", "none")
                is_prev_stacked_or_stitched = prev_stack_stitch in ("stack", "stitch")
            else:
                is_prev_stacked_or_stitched = False

            # If previous layer is stacked/stitched, disable this layer's stack/stitch
            # Also check if this layer is visible (checkbox enabled)
            is_visible = layer_control.visible_check.isChecked()

            if is_prev_stacked_or_stitched:
                # Disable stack/stitch and reset to "Independent"
                layer_control.stack_stitch_combo.setEnabled(False)
                layer_control.stack_stitch_combo.setCurrentIndex(0)  # "Independent"
            else:
                # Enable if layer is visible
                layer_control.stack_stitch_combo.setEnabled(is_visible)

    def _add_layer(self):
        """Add a new layer"""
        if self.num_visible_layers >= 8:
            return

        # Show the next hidden layer
        self.layer_controls[self.num_visible_layers].show()
        self.num_visible_layers += 1
        self._update_layer_buttons()

    def _remove_layer(self):
        """Remove the last layer"""
        if self.num_visible_layers <= 2:  # Keep at least Parent/Base + Layer 1
            return

        # Hide the last visible layer
        self.num_visible_layers -= 1
        layer_control = self.layer_controls[self.num_visible_layers]
        layer_control.hide()
        layer_control.set_layer_config(None)  # Clear its configuration
        self._update_layer_buttons()
        self._on_layer_changed()  # Update preview

    def _update_layer_buttons(self):
        """Update Add/Remove Layer button states"""
        self.add_layer_btn.setEnabled(self.num_visible_layers < 8)
        self.remove_layer_btn.setEnabled(self.num_visible_layers > 2)

        # Update move up/down button states for each visible layer
        for i in range(self.num_visible_layers):
            layer_control = self.layer_controls[i]
            # Parent/Base layer (index 0) can't move up
            layer_control.move_up_btn.setEnabled(i > 0)
            # Last visible layer can't move down
            layer_control.move_down_btn.setEnabled(i < self.num_visible_layers - 1)

        # Disable move buttons for hidden layers
        for i in range(self.num_visible_layers, 8):
            layer_control = self.layer_controls[i]
            layer_control.move_up_btn.setEnabled(False)
            layer_control.move_down_btn.setEnabled(False)

    def _move_layer_up(self, layer_index: int):
        """Move layer up (swap with layer above)"""
        if layer_index <= 0 or not self.current_composite:
            return

        # Swap configurations
        layers = self.current_composite.layers
        if layer_index < len(layers) and layer_index - 1 < len(layers):
            layers[layer_index], layers[layer_index - 1] = layers[layer_index - 1], layers[layer_index]

            # Reload UI
            self._load_composite_to_controls()
            self._update_preview()

    def _move_layer_down(self, layer_index: int):
        """Move layer down (swap with layer below)"""
        if layer_index >= self.num_visible_layers - 1 or not self.current_composite:
            return

        # Swap configurations
        layers = self.current_composite.layers
        if layer_index < len(layers) and layer_index + 1 < len(layers):
            layers[layer_index], layers[layer_index + 1] = layers[layer_index + 1], layers[layer_index]

            # Reload UI
            self._load_composite_to_controls()
            self._update_preview()

    def _update_composite_from_controls(self):
        """Update current composite from layer controls"""
        if not self.current_composite:
            return

        # Clear and rebuild layers
        self.current_composite.layers.clear()

        for layer_control in self.layer_controls:
            config = layer_control.get_layer_config()
            # get_layer_config() now always returns a dict, so just append it
            self.current_composite.layers.append(config)

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

    def _new_composite(self):
        """Create a new composite"""
        name, ok = QInputDialog.getText(self, "New Composite", "Enter composite name:")

        if ok and name:
            # Check if name already exists
            if self.project.get_composite(name):
                QMessageBox.warning(self, "Name Exists", f"A composite named '{name}' already exists.")
                return

            # Create new composite
            new_composite = LayerComposite(name)
            new_composite.fps = 60
            new_composite.loop = False

            # Add to project
            self.project.add_composite(new_composite)
            self.refresh_composite_list()

            # Select the new composite
            index = self.composite_combo.findText(name)
            if index >= 0:
                self.composite_combo.setCurrentIndex(index)

    def _rename_composite(self):
        """Rename current composite"""
        if not self.current_composite:
            return

        current_name = self.current_composite.name
        name, ok = QInputDialog.getText(
            self, "Rename Composite", "Enter new name:", text=current_name
        )

        if ok and name and name != current_name:
            # Check if name already exists
            if self.project.get_composite(name):
                QMessageBox.warning(self, "Name Exists", f"A composite named '{name}' already exists.")
                return

            # Rename
            self.current_composite.name = name
            self.refresh_composite_list()

            # Select the renamed composite
            index = self.composite_combo.findText(name)
            if index >= 0:
                self.composite_combo.setCurrentIndex(index)

    def _delete_composite(self):
        """Delete current composite"""
        composite = self.composite_combo.currentData()
        if not composite or composite not in self.project.composites:
            return

        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Delete Composite",
            f"Are you sure you want to delete '{composite.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self.project.composites.remove(composite)
            self.current_composite = None
            self.refresh_composite_list()

    def _toggle_playback(self):
        """Toggle play/pause"""
        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()

    def _on_speed_changed(self, fps: int):
        """Handle speed slider change"""
        # Update label
        self.speed_label.setText(f"{fps} fps")

        # If currently playing, update timer interval
        if self.is_playing:
            interval = int(1000 / fps)  # milliseconds
            self.timer.setInterval(interval)

    def _on_grid_changed(self, state):
        """Handle grid checkbox change"""
        self.preview_area.show_grid = (state == Qt.CheckState.Checked)
        self.preview_area.update()

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
