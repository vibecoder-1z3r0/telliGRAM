"""
Animation composer widget for multi-layer animation editing.

Manages multiple timeline editors and composite preview for layered animations.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal

from telligram.core.project import Project
from telligram.gui.widgets.timeline_editor_new import TimelineEditorWidget
from telligram.gui.widgets.composite_preview import CompositePreviewWidget


class AnimationComposerWidget(QWidget):
    """
    Multi-layer animation composer.

    Shows individual timeline editors for each layer plus composite preview.
    Starts in single-layer mode and expands to multi-layer when user adds layers.
    """

    animation_changed = Signal()  # Emitted when any animation changes

    def __init__(self, project: Project, main_window=None):
        super().__init__()
        self.project = project
        self.main_window = main_window
        self.timeline_editors = []
        self.is_multi_layer_mode = False

        self.setup_ui()

    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create vertically scrollable area for all content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container widget for scrollable content
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Timeline editors will be added here
        self.timeline_scroll_layout = self.scroll_layout

        # Create initial timeline editor
        self.add_timeline_editor()

        # Composite preview (initially hidden, will be added at bottom)
        self.composite_preview = CompositePreviewWidget(self.project)
        self.composite_preview.setVisible(False)
        self.scroll_layout.addWidget(self.composite_preview)

        # Add stretch at the end so content stays at top
        self.scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area, 1)

        # Layer management buttons (fixed at bottom)
        layer_btn_layout = QHBoxLayout()
        self.add_layer_btn = QPushButton("+ Add Layer")
        self.add_layer_btn.clicked.connect(self._add_layer)
        layer_btn_layout.addWidget(self.add_layer_btn)

        self.remove_layer_btn = QPushButton("- Remove Layer")
        self.remove_layer_btn.clicked.connect(self._remove_layer)
        self.remove_layer_btn.setEnabled(False)
        layer_btn_layout.addWidget(self.remove_layer_btn)

        layer_btn_layout.addStretch()
        layout.addLayout(layer_btn_layout)

    def add_timeline_editor(self):
        """Add a new timeline editor for a layer"""
        editor = TimelineEditorWidget(main_window=self.main_window)
        editor.set_project(self.project)
        editor.animation_changed.connect(self.animation_changed.emit)
        editor.animation_changed.connect(self._update_composite_preview)

        # Add to layout - insert BEFORE the composite preview
        # The layout order is: timeline1, timeline2, ..., composite_preview, stretch
        insert_pos = len(self.timeline_editors)
        self.timeline_scroll_layout.insertWidget(insert_pos, editor)

        self.timeline_editors.append(editor)

        return editor

    def remove_timeline_editor(self, index: int):
        """Remove a timeline editor"""
        if 0 <= index < len(self.timeline_editors):
            editor = self.timeline_editors.pop(index)
            self.timeline_scroll_layout.removeWidget(editor)
            editor.deleteLater()

    def _add_layer(self):
        """Add a new layer"""
        if len(self.timeline_editors) >= 8:
            return  # Maximum 8 layers

        self.add_timeline_editor()

        # Enable multi-layer mode if we have more than 1 layer
        if len(self.timeline_editors) > 1:
            self._enable_multi_layer_mode()

        # Update button states
        self.remove_layer_btn.setEnabled(len(self.timeline_editors) > 1)

    def _remove_layer(self):
        """Remove the last layer"""
        if len(self.timeline_editors) <= 1:
            return  # Keep at least one layer

        self.remove_timeline_editor(len(self.timeline_editors) - 1)

        # Disable multi-layer mode if back to 1 layer
        if len(self.timeline_editors) == 1:
            self._disable_multi_layer_mode()

        # Update button states
        self.remove_layer_btn.setEnabled(len(self.timeline_editors) > 1)

    def _enable_multi_layer_mode(self):
        """Enable multi-layer mode - show composite preview"""
        if self.is_multi_layer_mode:
            return

        self.is_multi_layer_mode = True
        self.composite_preview.setVisible(True)
        self.composite_preview.update_animations()
        self._update_composite_preview()

    def _disable_multi_layer_mode(self):
        """Disable multi-layer mode - hide composite preview"""
        if not self.is_multi_layer_mode:
            return

        self.is_multi_layer_mode = False
        self.composite_preview.setVisible(False)

    def _update_composite_preview(self):
        """Update composite preview when animations change"""
        if not self.is_multi_layer_mode:
            return

        # Update animation list in composite preview
        self.composite_preview.update_animations()

    def set_project(self, project: Project):
        """Set the project for all editors"""
        self.project = project

        for editor in self.timeline_editors:
            editor.set_project(project)

        self.composite_preview.project = project
        self.composite_preview.update_animations()
        self.composite_preview.refresh_composite_list()

    def refresh(self):
        """Refresh all editors"""
        for editor in self.timeline_editors:
            if editor.current_animation:
                editor._load_animation(editor.current_animation)
            editor._refresh_animation_list()

        if self.is_multi_layer_mode:
            self.composite_preview.update_animations()
            self.composite_preview.refresh_composite_list()

    def set_current_card_slot(self, slot: int):
        """
        Set current card slot for the primary (first) timeline editor.

        This maintains compatibility with single-layer workflow.
        """
        if self.timeline_editors:
            self.timeline_editors[0].set_current_card_slot(slot)

    @property
    def current_animation(self):
        """
        Get current animation from the primary (first) timeline editor.

        This maintains compatibility with animation export functionality.
        """
        if self.timeline_editors:
            return self.timeline_editors[0].current_animation
        return None

    @property
    def animation_combo(self):
        """
        Get animation combo box from the primary timeline editor.

        This maintains compatibility with undo/redo commands.
        """
        if self.timeline_editors:
            return self.timeline_editors[0].animation_combo
        return None

    def _load_animation(self, animation):
        """
        Load animation in the primary timeline editor.

        This maintains compatibility with undo/redo commands.
        """
        if self.timeline_editors:
            self.timeline_editors[0]._load_animation(animation)

    def _refresh_animation_list(self):
        """
        Refresh animation list in the primary timeline editor.

        This maintains compatibility with undo/redo commands.
        """
        if self.timeline_editors:
            self.timeline_editors[0]._refresh_animation_list()
