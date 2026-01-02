"""Main application window for telliGRAM"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QFileDialog, QMessageBox, QStatusBar,
    QLabel, QPushButton, QTabWidget, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QUndoStack, QUndoCommand
from pathlib import Path

from telligram.core.project import Project
from telligram.gui.widgets.card_grid import CardGridWidget
from telligram.gui.widgets.pixel_editor import PixelEditorWidget
from telligram.gui.widgets.grom_browser import GromBrowserWidget
from telligram.gui.widgets.timeline_editor_new import TimelineEditorWidget
from telligram.gui.widgets.animation_composer import AnimationComposerWidget
from telligram.gui.widgets.color_palette import ColorPaletteWidget


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.project = Project(name="Untitled")
        self.current_file = None
        self.current_card_slot = 0
        self.undo_stack = QUndoStack(self)

        self.setWindowTitle("telliGRAM v0.1.0-alpha - Intellivision GRAM Card Creator and Animator")
        self.setMinimumSize(1200, 800)
        self.resize(1750, 880)  # Default window size with proper spacing

        self._create_menu_bar()
        self._create_widgets()
        self._create_status_bar()
        self._connect_signals()
        self._initialize_widgets()

    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Project...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Export submenu
        export_menu = file_menu.addMenu("&Export All Cards")

        export_intybasic_visual_action = QAction("IntyBASIC (Visual)...", self)
        export_intybasic_visual_action.triggered.connect(self.export_all_intybasic_visual)
        export_menu.addAction(export_intybasic_visual_action)

        export_intybasic_data_action = QAction("IntyBASIC (Data)...", self)
        export_intybasic_data_action.triggered.connect(self.export_all_intybasic_data)
        export_menu.addAction(export_intybasic_data_action)

        export_menu.addSeparator()

        export_mbcc_action = QAction("MBCC...", self)
        export_mbcc_action.triggered.connect(self.export_all_mbcc)
        export_menu.addAction(export_mbcc_action)

        export_menu.addSeparator()

        export_asm_action = QAction("Assembly (DECLE)...", self)
        export_asm_action.triggered.connect(self.export_all_asm)
        export_menu.addAction(export_asm_action)

        # Export Animation submenu
        export_anim_menu = file_menu.addMenu("Export &Animation")

        export_anim_intybasic_action = QAction("IntyBASIC...", self)
        export_anim_intybasic_action.triggered.connect(self.export_animation_intybasic)
        export_anim_menu.addAction(export_anim_intybasic_action)

        export_anim_mbcc_action = QAction("MBCC...", self)
        export_anim_mbcc_action.triggered.connect(self.export_animation_mbcc)
        export_anim_menu.addAction(export_anim_mbcc_action)

        export_anim_asm_action = QAction("Assembly (DECLE)...", self)
        export_anim_asm_action.triggered.connect(self.export_animation_asm)
        export_anim_menu.addAction(export_anim_asm_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Undo/Redo actions
        undo_action = self.undo_stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = self.undo_stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut("Ctrl+Shift+Z")
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        clear_card_action = QAction("&Clear Card", self)
        clear_card_action.setShortcut("Ctrl+Shift+C")
        clear_card_action.triggered.connect(self.clear_current_card)
        edit_menu.addAction(clear_card_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_widgets(self):
        """Create main widgets"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignTop)

        # Left panel - GRAM Card grid and pixel editor
        left_panel = QWidget()
        left_panel_layout = QHBoxLayout(left_panel)
        left_panel_layout.setAlignment(Qt.AlignTop)

        # GRAM Card grid
        grid_panel = QWidget()
        grid_layout = QVBoxLayout(grid_panel)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(QLabel("<h3>GRAM Cards (64 slots)</h3>"))

        self.card_grid = CardGridWidget(main_window=self)
        grid_layout.addWidget(self.card_grid)

        # Info label
        self.cards_info_label = QLabel("Cards used: 0/64")
        grid_layout.addWidget(self.cards_info_label)

        left_panel_layout.addWidget(grid_panel, stretch=1)

        # Pixel editor
        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        self.card_label = QLabel("<h3>Card #0</h3>")
        editor_layout.addWidget(self.card_label)

        self.pixel_editor = PixelEditorWidget(main_window=self)
        editor_layout.addWidget(self.pixel_editor)

        # Buttons
        button_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear Card")
        clear_btn.clicked.connect(self.clear_current_card)
        button_layout.addWidget(clear_btn)

        flip_h_btn = QPushButton("Flip H")
        flip_h_btn.clicked.connect(self.flip_horizontal)
        button_layout.addWidget(flip_h_btn)

        flip_v_btn = QPushButton("Flip V")
        flip_v_btn.clicked.connect(self.flip_vertical)
        button_layout.addWidget(flip_v_btn)

        editor_layout.addLayout(button_layout)

        # Color palette
        self.color_label = QLabel("<b>Color (#7):</b>")
        editor_layout.addWidget(self.color_label)
        self.color_palette = ColorPaletteWidget()
        editor_layout.addWidget(self.color_palette)

        editor_layout.addStretch()

        left_panel_layout.addWidget(editor_panel, stretch=2)

        # Set left panel to a fixed/maximum width so it doesn't resize
        # Provides proper spacing for GRAM card grid and pixel editor
        left_panel.setMaximumWidth(1000)

        main_layout.addWidget(left_panel, stretch=0)  # Don't stretch

        # Right panel - IntelliMation Station
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 3, 0, 0)  # Add 3px top margin to align with other headers

        right_layout.addWidget(QLabel("<h3>IntelliMation Station</h3>"))

        self.timeline_editor = AnimationComposerWidget(project=self.project, main_window=self)
        right_layout.addWidget(self.timeline_editor)

        main_layout.addWidget(right_panel, stretch=1)  # Takes remaining space

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self):
        """Connect widget signals"""
        self.card_grid.card_selected.connect(self.on_card_selected)
        self.pixel_editor.card_changed.connect(self.on_card_changed)
        self.undo_stack.cleanChanged.connect(self.update_title)
        self.timeline_editor.animation_changed.connect(self.on_animation_changed)
        self.color_palette.color_selected.connect(self.on_color_selected)

    def _initialize_widgets(self):
        """Initialize widgets with default project data"""
        self.card_grid.set_project(self.project)
        self.timeline_editor.set_project(self.project)
        self.update_title()
        self.update_cards_info()

    def _on_tab_changed(self, index: int):
        """Handle tab change - GROM browser disabled for WSL compatibility"""
        # GROM browser lazy loading disabled
        pass

    def new_project(self):
        """Create new project"""
        # TODO: Ask to save current project if modified
        self.project = Project(name="Untitled")
        self.current_file = None
        self.card_grid.set_project(self.project)
        self.pixel_editor.set_card(None)
        self.timeline_editor.set_project(self.project)
        self.undo_stack.setClean()
        self.update_title()
        self.update_cards_info()
        self.status_bar.showMessage("New project created")

    def open_project(self):
        """Open project from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "telliGRAM Projects (*.telligram);;All Files (*)"
        )

        if filename:
            try:
                self.project = Project.load(Path(filename))
                self.current_file = Path(filename)
                self.card_grid.set_project(self.project)
                # Sync main window state to card 0 (which card_grid selects)
                self.on_card_selected(0)
                self.timeline_editor.set_project(self.project)
                self.undo_stack.setClean()
                self.update_title()
                self.update_cards_info()
                self.status_bar.showMessage(f"Opened: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project:\n{e}")

    def save_project(self):
        """Save current project"""
        if self.current_file is None:
            self.save_project_as()
        else:
            try:
                self.project.save(self.current_file)
                self.undo_stack.setClean()
                self.update_title()
                self.status_bar.showMessage(f"Saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project:\n{e}")

    def save_project_as(self):
        """Save project to new file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            "",
            "telliGRAM Projects (*.telligram);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.telligram'):
                filename += '.telligram'

            try:
                self.current_file = Path(filename)
                self.project.save(self.current_file)
                self.undo_stack.setClean()
                self.update_title()
                self.status_bar.showMessage(f"Saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project:\n{e}")

    def on_card_selected(self, slot: int):
        """Handle card selection from grid"""
        self.current_card_slot = slot
        card = self.project.get_card(slot)
        self.pixel_editor.set_card(card)
        self.card_label.setText(f"<h3>Card #{slot} (GRAM {256 + slot})</h3>")
        self.timeline_editor.set_current_card_slot(slot)

        # Update color palette to show this card's color
        if card is not None and hasattr(card, 'color'):
            self.color_palette.set_color(card.color)
            self.color_label.setText(f"<b>Color (#{card.color}):</b>")

    def on_color_selected(self, color_index: int):
        """Handle color selection from palette"""
        card = self.project.get_card(self.current_card_slot)
        if card is not None:
            old_color = card.color if hasattr(card, 'color') else 7
            if old_color != color_index:
                # Create undoable command
                command = ChangeCardColorCommand(self, self.current_card_slot, old_color, color_index)
                self.undo_stack.push(command)
                # Update color label
                self.color_label.setText(f"<b>Color (#{color_index}):</b>")

    def on_card_changed(self):
        """Handle card modification in pixel editor"""
        # Save card back to project
        card = self.pixel_editor.get_card()
        if card is not None:
            # If card is empty, clear the slot instead of saving an empty card
            if card.is_empty():
                self.project.clear_card(self.current_card_slot)
                self.card_grid.update_card(self.current_card_slot, None)
            else:
                self.project.set_card(self.current_card_slot, card)
                self.card_grid.update_card(self.current_card_slot, card)
            self.update_cards_info()

    def clear_current_card(self):
        """Clear current card"""
        command = ClearCardCommand(self, self.current_card_slot)
        self.undo_stack.push(command)

    def flip_horizontal(self):
        """Flip current card horizontally"""
        command = FlipHorizontalCommand(self, self.current_card_slot)
        self.undo_stack.push(command)

    def flip_vertical(self):
        """Flip current card vertically"""
        command = FlipVerticalCommand(self, self.current_card_slot)
        self.undo_stack.push(command)

    def update_title(self):
        """Update window title"""
        title = "telliGRAM v0.1.0-alpha"
        if self.current_file:
            title += f" - {self.current_file.name}"
        else:
            title += " - Untitled"

        # Add asterisk if project has unsaved changes
        if not self.undo_stack.isClean():
            title += " *"

        self.setWindowTitle(title)

    def update_cards_info(self):
        """Update cards info label"""
        count = self.project.get_card_count()
        self.cards_info_label.setText(f"Cards used: {count}/64")

    def on_animation_changed(self):
        """Handle animation modification"""
        # Animation changes go through undo stack, so this is just for UI updates
        pass

    # Animation undo-able operations
    def create_animation_undoable(self, name: str):
        """Create animation with undo support"""
        command = CreateAnimationCommand(self, name)
        self.undo_stack.push(command)
        return command.animation

    def rename_animation_undoable(self, animation, old_name: str, new_name: str):
        """Rename animation with undo support"""
        command = RenameAnimationCommand(self, animation, old_name, new_name)
        self.undo_stack.push(command)

    def delete_animation_undoable(self, animation, index: int):
        """Delete animation with undo support"""
        command = DeleteAnimationCommand(self, animation, index)
        self.undo_stack.push(command)

    def add_frame_undoable(self, animation, card_slot: int, duration: int):
        """Add frame with undo support"""
        command = AddFrameCommand(self, animation, card_slot, duration)
        self.undo_stack.push(command)

    def insert_frame_undoable(self, animation, index: int, card_slot: int, duration: int):
        """Insert frame with undo support"""
        command = InsertFrameCommand(self, animation, index, card_slot, duration)
        self.undo_stack.push(command)

    def remove_frame_undoable(self, animation, index: int):
        """Remove frame with undo support"""
        command = RemoveFrameCommand(self, animation, index)
        self.undo_stack.push(command)

    def change_frame_duration_undoable(self, animation, frame_index: int, old_duration: int, new_duration: int):
        """Change frame duration with undo support"""
        command = ChangeFrameDurationCommand(self, animation, frame_index, old_duration, new_duration)
        self.undo_stack.push(command)

    def reorder_frame_undoable(self, animation, from_index: int, to_index: int):
        """Reorder frame with undo support"""
        command = ReorderFrameCommand(self, animation, from_index, to_index)
        self.undo_stack.push(command)

    def duplicate_frame_undoable(self, animation, index: int):
        """Duplicate frame with undo support"""
        command = DuplicateFrameCommand(self, animation, index)
        self.undo_stack.push(command)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About telliGRAM",
            "<h2>telliGRAM v0.1.0-alpha</h2>"
            "<p>Intellivision GRAM Card Creator and Animator</p>"
            "<p>Create custom 8×8 graphics and animations for Intellivision games</p>"
            "<p>© 2025-2026 Andrew Potozniak (Tyraziel & 1.z3r0)</p>"
            "<p>Licensed under the MIT License</p>"
            "<p><i>Developed with AI assistance from Anthropic Claude</i></p>"
        )

    def export_all_intybasic_visual(self):
        """Export all cards as IntyBASIC code (visual format)"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export All Cards (IntyBASIC Visual)",
            "",
            "IntyBASIC Source (*.bas);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.bas'):
                filename += '.bas'

            try:
                code = self._generate_all_cards_intybasic_visual()
                with open(filename, 'w') as f:
                    f.write(code)
                self.status_bar.showMessage(f"Exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export cards:\n{e}")

    def export_all_intybasic_data(self):
        """Export all cards as IntyBASIC code (DATA format)"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export All Cards (IntyBASIC Data)",
            "",
            "IntyBASIC Source (*.bas);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.bas'):
                filename += '.bas'

            try:
                code = self._generate_all_cards_intybasic_data()
                with open(filename, 'w') as f:
                    f.write(code)
                self.status_bar.showMessage(f"Exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export cards:\n{e}")

    def export_all_mbcc(self):
        """Export all cards as MBCC code"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export All Cards (MBCC)",
            "",
            "C Header (*.h);;C Source (*.c);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.h') and not filename.endswith('.c'):
                filename += '.h'

            try:
                code = self._generate_all_cards_mbcc()
                with open(filename, 'w') as f:
                    f.write(code)
                self.status_bar.showMessage(f"Exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export cards:\n{e}")

    def export_all_asm(self):
        """Export all cards as Assembly code"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export All Cards (Assembly)",
            "",
            "Assembly Source (*.asm);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.asm'):
                filename += '.asm'

            try:
                code = self._generate_all_cards_asm()
                with open(filename, 'w') as f:
                    f.write(code)
                self.status_bar.showMessage(f"Exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export cards:\n{e}")

    def _generate_all_cards_intybasic_visual(self) -> str:
        """Generate IntyBASIC code for all non-empty cards (visual format)"""
        code = "' telliGRAM Export - All GRAM Cards (Visual Format)\n"
        code += f"' Project: {self.current_file.name if self.current_file else 'Untitled'}\n\n"

        card_count = 0
        for slot in range(64):
            card = self.project.get_card(slot)
            if card is not None and not card.is_empty():
                # Get card data as binary strings
                binary_rows = card.to_binary_strings()

                # Convert to visual representation (1 -> X, 0 -> .)
                visual_rows = []
                for row in binary_rows:
                    visual_row = row.replace('1', 'X').replace('0', '.')
                    visual_rows.append(f'    "{visual_row}"')

                code += f"' GRAM Card #{slot} (slot {256 + slot})\n"
                code += f"BITMAP card_{slot}\n"
                code += "\n".join(visual_rows)
                code += "\nEND\n\n"
                card_count += 1

        code += f"' Total cards exported: {card_count}\n"
        return code

    def _generate_all_cards_intybasic_data(self) -> str:
        """Generate IntyBASIC code for all non-empty cards (DATA format)"""
        code = "' telliGRAM Export - All GRAM Cards (Data Format)\n"
        code += f"' Project: {self.current_file.name if self.current_file else 'Untitled'}\n\n"

        card_count = 0
        for slot in range(64):
            card = self.project.get_card(slot)
            if card is not None and not card.is_empty():
                data = card.to_bytes()

                code += f"' GRAM Card #{slot} (slot {256 + slot})\n"
                code += f"BITMAP card_{slot}\n"
                code += "    DATA "
                code += ", ".join(f"${byte:02X}" for byte in data)
                code += "\nEND\n\n"
                card_count += 1

        code += f"' Total cards exported: {card_count}\n"
        return code

    def _generate_all_cards_mbcc(self) -> str:
        """Generate MBCC code for all non-empty cards"""
        code = "// telliGRAM Export - All GRAM Cards (MBCC)\n"
        code += f"// Project: {self.current_file.name if self.current_file else 'Untitled'}\n\n"

        # Collect all non-empty cards
        cards = []
        for slot in range(64):
            card = self.project.get_card(slot)
            if card is not None and not card.is_empty():
                cards.append((slot, card))

        # Generate array declaration
        code += f"const U16 my_gram[] = {{\n"

        for i, (slot, card) in enumerate(cards):
            # Get card data as binary strings
            binary_rows = card.to_binary_strings()

            # Convert to visual representation (1 -> #, 0 -> .)
            visual_rows = []
            for row in binary_rows:
                visual_row = row.replace('1', '#').replace('0', '.')
                visual_rows.append(f'            "{visual_row}"')

            # Add comment
            code += f"    // GRAM Card #{slot} (slot {256 + slot})\n"
            code += "    SBITMAP(\n"
            code += ",\n".join(visual_rows)
            code += ")"

            # Add comma if not last element
            if i < len(cards) - 1:
                code += ","

            code += "\n"

        code += "};\n\n"
        code += f"// Total cards exported: {len(cards)}\n"
        return code

    def _generate_all_cards_asm(self) -> str:
        """Generate Assembly code for all non-empty cards"""
        code = "; telliGRAM Export - All GRAM Cards (Assembly)\n"
        code += f"; Project: {self.current_file.name if self.current_file else 'Untitled'}\n\n"

        card_count = 0
        for slot in range(64):
            card = self.project.get_card(slot)
            if card is not None and not card.is_empty():
                data = card.to_bytes()

                code += f"; GRAM Card #{slot} (slot {256 + slot})\n"
                code += f"card_{slot}:\n"

                for i in range(0, 8, 2):
                    low_byte = data[i]
                    high_byte = data[i + 1] if i + 1 < 8 else 0
                    decle = (high_byte << 8) | low_byte
                    code += f"    DECLE ${decle:04X}    ; rows {i}-{i+1}\n"

                code += "\n"
                card_count += 1

        code += f"; Total cards exported: {card_count}\n"
        return code

    def export_animation_intybasic(self):
        """Export current animation as IntyBASIC code"""
        if not self.timeline_editor or not self.timeline_editor.current_animation:
            QMessageBox.warning(self, "No Animation", "Please select an animation to export.")
            return

        anim = self.timeline_editor.current_animation

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Animation (IntyBASIC)",
            f"{anim.name}.bas",
            "IntyBASIC Source (*.bas);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.bas'):
                filename += '.bas'

            try:
                code = self._generate_animation_intybasic(anim)
                with open(filename, 'w') as f:
                    f.write(code)
                self.status_bar.showMessage(f"Exported animation to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export animation:\n{e}")

    def export_animation_mbcc(self):
        """Export current animation as MBCC code"""
        if not self.timeline_editor or not self.timeline_editor.current_animation:
            QMessageBox.warning(self, "No Animation", "Please select an animation to export.")
            return

        anim = self.timeline_editor.current_animation

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Animation (MBCC)",
            f"{anim.name}.h",
            "C Header (*.h);;C Source (*.c);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.h') and not filename.endswith('.c'):
                filename += '.h'

            try:
                code = self._generate_animation_mbcc(anim)
                with open(filename, 'w') as f:
                    f.write(code)
                self.status_bar.showMessage(f"Exported animation to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export animation:\n{e}")

    def export_animation_asm(self):
        """Export current animation as Assembly code"""
        if not self.timeline_editor or not self.timeline_editor.current_animation:
            QMessageBox.warning(self, "No Animation", "Please select an animation to export.")
            return

        anim = self.timeline_editor.current_animation

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Animation (Assembly)",
            f"{anim.name}.asm",
            "Assembly Source (*.asm);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.asm'):
                filename += '.asm'

            try:
                code = self._generate_animation_asm(anim)
                with open(filename, 'w') as f:
                    f.write(code)
                self.status_bar.showMessage(f"Exported animation to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export animation:\n{e}")

    def _generate_animation_intybasic(self, anim) -> str:
        """Generate IntyBASIC code for animation"""
        code = f"' telliGRAM Animation Export\n"
        code += f"' Animation: {anim.name}\n"
        code += f"' Frames: {anim.frame_count}, FPS: {anim.fps}, Loop: {anim.loop}\n\n"

        # Collect unique cards used in animation
        unique_cards = {}
        for i in range(anim.frame_count):
            frame = anim.get_frame(i)
            card_slot = frame["card_slot"]
            if card_slot not in unique_cards:
                card = self.project.get_card(card_slot)
                if card is not None:
                    unique_cards[card_slot] = card

        # Export card definitions
        code += "' Card definitions used in animation\n"
        for slot in sorted(unique_cards.keys()):
            card = unique_cards[slot]
            binary_rows = card.to_binary_strings()
            visual_rows = []
            for row in binary_rows:
                visual_row = row.replace('1', 'X').replace('0', '.')
                visual_rows.append(f'    "{visual_row}"')

            code += f"BITMAP {anim.name}_card_{slot}\n"
            code += "\n".join(visual_rows)
            code += "\nEND\n\n"

        # Export animation frame sequence
        code += f"' Animation frame sequence (frame index, card slot, duration)\n"
        code += f"' FPS: {anim.fps} (interval: {1000 // anim.fps}ms per frame)\n"
        code += f"{anim.name}_frames:\n"
        code += "    DATA "
        code += str(anim.frame_count)
        code += f"  ' Number of frames\n"

        for i in range(anim.frame_count):
            frame = anim.get_frame(i)
            code += f"    DATA {frame['card_slot']}, {frame['duration']}"
            code += f"  ' Frame {i}: slot {frame['card_slot']}, duration {frame['duration']}\n"

        code += f"\n' Usage: Loop through frames, load each card for specified duration\n"
        code += f"' Loop mode: {anim.loop}\n"

        return code

    def _generate_animation_mbcc(self, anim) -> str:
        """Generate MBCC code for animation"""
        code = f"// telliGRAM Animation Export\n"
        code += f"// Animation: {anim.name}\n"
        code += f"// Frames: {anim.frame_count}, FPS: {anim.fps}, Loop: {anim.loop}\n\n"

        # Collect unique cards
        unique_cards = {}
        for i in range(anim.frame_count):
            frame = anim.get_frame(i)
            card_slot = frame["card_slot"]
            if card_slot not in unique_cards:
                card = self.project.get_card(card_slot)
                if card is not None:
                    unique_cards[card_slot] = card

        # Export card definitions
        code += "// Card definitions used in animation\n"
        for slot in sorted(unique_cards.keys()):
            card = unique_cards[slot]
            binary_rows = card.to_binary_strings()
            visual_rows = []
            for row in binary_rows:
                visual_row = row.replace('1', '#').replace('0', '.')
                visual_rows.append(f'        "{visual_row}"')

            code += f"const U16 {anim.name}_card_{slot} = SBITMAP(\n"
            code += ",\n".join(visual_rows)
            code += ");\n\n"

        # Export animation frame sequence
        code += f"// Animation frame data\n"
        code += f"typedef struct {{\n"
        code += f"    U16 card_slot;\n"
        code += f"    U16 duration;\n"
        code += f"}} AnimFrame;\n\n"

        code += f"const AnimFrame {anim.name}_frames[] = {{\n"
        for i in range(anim.frame_count):
            frame = anim.get_frame(i)
            code += f"    {{{frame['card_slot']}, {frame['duration']}}}"
            if i < anim.frame_count - 1:
                code += ","
            code += f"  // Frame {i}\n"
        code += "};\n\n"

        code += f"#define {anim.name.upper()}_FRAME_COUNT {anim.frame_count}\n"
        code += f"#define {anim.name.upper()}_FPS {anim.fps}\n"
        code += f"#define {anim.name.upper()}_LOOP {1 if anim.loop else 0}\n"

        return code

    def _generate_animation_asm(self, anim) -> str:
        """Generate Assembly code for animation"""
        code = f"; telliGRAM Animation Export\n"
        code += f"; Animation: {anim.name}\n"
        code += f"; Frames: {anim.frame_count}, FPS: {anim.fps}, Loop: {anim.loop}\n\n"

        # Collect unique cards
        unique_cards = {}
        for i in range(anim.frame_count):
            frame = anim.get_frame(i)
            card_slot = frame["card_slot"]
            if card_slot not in unique_cards:
                card = self.project.get_card(card_slot)
                if card is not None:
                    unique_cards[card_slot] = card

        # Export card definitions
        code += "; Card definitions used in animation\n"
        for slot in sorted(unique_cards.keys()):
            card = unique_cards[slot]
            data = card.to_bytes()

            code += f"{anim.name}_card_{slot}:\n"
            for i in range(0, 8, 2):
                low_byte = data[i]
                high_byte = data[i + 1] if i + 1 < 8 else 0
                decle = (high_byte << 8) | low_byte
                code += f"    DECLE ${decle:04X}\n"
            code += "\n"

        # Export animation frame sequence
        code += f"; Animation frame data (card_slot, duration pairs)\n"
        code += f"{anim.name}_frames:\n"
        code += f"    DECLE {anim.frame_count}  ; Frame count\n"

        for i in range(anim.frame_count):
            frame = anim.get_frame(i)
            code += f"    DECLE {frame['card_slot']}, {frame['duration']}"
            code += f"  ; Frame {i}\n"

        code += f"\n; Animation properties\n"
        code += f"{anim.name}_fps:    DECLE {anim.fps}\n"
        code += f"{anim.name}_loop:   DECLE {1 if anim.loop else 0}\n"

        return code

    def closeEvent(self, event):
        """Handle window close event"""
        # TODO: Ask to save if project has unsaved changes
        event.accept()
        QApplication.quit()


# Undo/Redo Command Classes

class CardOperationCommand(QUndoCommand):
    """Base class for card operation commands"""

    def __init__(self, main_window, slot, description):
        super().__init__(description)
        self.main_window = main_window
        self.slot = slot
        self.old_data = None
        self.new_data = None

        # Store current card state
        card = main_window.project.get_card(slot)
        if card is not None:
            self.old_data = card.to_bytes()

    def undo(self):
        """Restore old card state"""
        if self.old_data is not None:
            from telligram.core.card import GramCard
            card = GramCard(data=self.old_data)
            self.main_window.project.set_card(self.slot, card)
            self.main_window.card_grid.update_card(self.slot, card)
            # Update pixel editor if this is the current card
            if self.main_window.current_card_slot == self.slot:
                self.main_window.pixel_editor.set_card(card)

    def redo(self):
        """Apply new card state"""
        if self.new_data is not None:
            from telligram.core.card import GramCard
            card = GramCard(data=self.new_data)
            self.main_window.project.set_card(self.slot, card)
            self.main_window.card_grid.update_card(self.slot, card)
            # Update pixel editor if this is the current card
            if self.main_window.current_card_slot == self.slot:
                self.main_window.pixel_editor.set_card(card)


class ClearCardCommand(CardOperationCommand):
    """Command for clearing a card"""

    def __init__(self, main_window, slot):
        super().__init__(main_window, slot, f"Clear Card #{slot}")

        # Calculate new state without modifying original
        from telligram.core.card import GramCard
        self.new_data = [0] * 8  # Empty card


class FlipHorizontalCommand(CardOperationCommand):
    """Command for flipping a card horizontally"""

    def __init__(self, main_window, slot):
        super().__init__(main_window, slot, f"Flip Horizontal Card #{slot}")

        # Calculate new state without modifying original
        from telligram.core.card import GramCard
        card = main_window.project.get_card(slot)
        if card is not None:
            # Create a copy and flip it
            temp_card = GramCard(data=card.to_bytes())
            temp_card.flip_horizontal()
            self.new_data = temp_card.to_bytes()


class FlipVerticalCommand(CardOperationCommand):
    """Command for flipping a card vertically"""

    def __init__(self, main_window, slot):
        super().__init__(main_window, slot, f"Flip Vertical Card #{slot}")

        # Calculate new state without modifying original
        from telligram.core.card import GramCard
        card = main_window.project.get_card(slot)
        if card is not None:
            # Create a copy and flip it
            temp_card = GramCard(data=card.to_bytes())
            temp_card.flip_vertical()
            self.new_data = temp_card.to_bytes()


class PasteCardCommand(CardOperationCommand):
    """Command for pasting a card"""

    def __init__(self, main_window, slot, card_data):
        super().__init__(main_window, slot, f"Paste Card #{slot}")
        self.new_data = card_data


class PixelEditCommand(CardOperationCommand):
    """Command for pixel editing (entire stroke from press to release)"""

    def __init__(self, main_window, slot, old_data, new_data):
        # Don't call super().__init__ because we already have the data
        QUndoCommand.__init__(self, f"Edit Card #{slot}")
        self.main_window = main_window
        self.slot = slot
        self.old_data = old_data
        self.new_data = new_data

    def undo(self):
        """Restore old card state"""
        if self.old_data is not None:
            from telligram.core.card import GramCard
            card = GramCard(data=self.old_data)
            self.main_window.project.set_card(self.slot, card)
            self.main_window.card_grid.update_card(self.slot, card)
            # Update pixel editor if this is the current card
            if self.main_window.current_card_slot == self.slot:
                self.main_window.pixel_editor.set_card(card)

    def redo(self):
        """Apply new card state"""
        if self.new_data is not None:
            from telligram.core.card import GramCard
            card = GramCard(data=self.new_data)
            self.main_window.project.set_card(self.slot, card)
            self.main_window.card_grid.update_card(self.slot, card)
            # Update pixel editor if this is the current card
            if self.main_window.current_card_slot == self.slot:
                self.main_window.pixel_editor.set_card(card)


class ChangeCardColorCommand(QUndoCommand):
    """Command for changing a card's color"""

    def __init__(self, main_window, slot, old_color, new_color):
        super().__init__(f"Change Color Card #{slot}")
        self.main_window = main_window
        self.slot = slot
        self.old_color = old_color
        self.new_color = new_color

    def undo(self):
        """Restore old color"""
        card = self.main_window.project.get_card(self.slot)
        if card is not None:
            card.color = self.old_color
            self.main_window.card_grid.update_card(self.slot, card)
            # Update pixel editor if this is the current card
            if self.main_window.current_card_slot == self.slot:
                self.main_window.pixel_editor.set_card(card)
                # Update color palette selection
                if hasattr(self.main_window, 'color_palette'):
                    self.main_window.color_palette.set_color(self.old_color)
                # Update color label
                if hasattr(self.main_window, 'color_label'):
                    self.main_window.color_label.setText(f"<b>Color (#{self.old_color}):</b>")
            # Update timeline if needed
            if self.main_window.timeline_editor.current_animation:
                self.main_window.timeline_editor._load_animation(
                    self.main_window.timeline_editor.current_animation
                )

    def redo(self):
        """Apply new color"""
        card = self.main_window.project.get_card(self.slot)
        if card is not None:
            card.color = self.new_color
            self.main_window.card_grid.update_card(self.slot, card)
            # Update pixel editor if this is the current card
            if self.main_window.current_card_slot == self.slot:
                self.main_window.pixel_editor.set_card(card)
                # Update color palette selection
                if hasattr(self.main_window, 'color_palette'):
                    self.main_window.color_palette.set_color(self.new_color)
                # Update color label
                if hasattr(self.main_window, 'color_label'):
                    self.main_window.color_label.setText(f"<b>Color (#{self.new_color}):</b>")
            # Update timeline if needed
            if self.main_window.timeline_editor.current_animation:
                self.main_window.timeline_editor._load_animation(
                    self.main_window.timeline_editor.current_animation
                )


# Animation Undo/Redo Command Classes

class CreateAnimationCommand(QUndoCommand):
    """Command for creating a new animation"""

    def __init__(self, main_window, animation_name):
        super().__init__(f"Create Animation '{animation_name}'")
        self.main_window = main_window
        self.animation_name = animation_name
        self.animation = None

    def redo(self):
        """Create the animation"""
        from telligram.core.animation import Animation
        self.animation = Animation(name=self.animation_name)
        self.main_window.project.add_animation(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()
        # Select the newly created animation
        index = len(self.main_window.project.animations) - 1
        self.main_window.timeline_editor.animation_combo.setCurrentIndex(index)
        # Manually load since signals are blocked during refresh
        self.main_window.timeline_editor._load_animation(self.animation)

    def undo(self):
        """Remove the animation"""
        if self.animation in self.main_window.project.animations:
            self.main_window.project.animations.remove(self.animation)
            self.main_window.timeline_editor._refresh_animation_list()
            # Select first animation if any exist
            if len(self.main_window.project.animations) > 0:
                self.main_window.timeline_editor.animation_combo.setCurrentIndex(0)
                # Manually load since signals are blocked during refresh
                self.main_window.timeline_editor._load_animation(self.main_window.project.animations[0])
            else:
                self.main_window.timeline_editor._load_animation(None)


class RenameAnimationCommand(QUndoCommand):
    """Command for renaming an animation"""

    def __init__(self, main_window, animation, old_name, new_name):
        super().__init__(f"Rename Animation '{old_name}' to '{new_name}'")
        self.main_window = main_window
        self.animation = animation
        self.old_name = old_name
        self.new_name = new_name

    def redo(self):
        """Apply new name"""
        self.animation.name = self.new_name
        self.main_window.timeline_editor._refresh_animation_list()

    def undo(self):
        """Restore old name"""
        self.animation.name = self.old_name
        self.main_window.timeline_editor._refresh_animation_list()


class DeleteAnimationCommand(QUndoCommand):
    """Command for deleting an animation"""

    def __init__(self, main_window, animation, animation_index):
        super().__init__(f"Delete Animation '{animation.name}'")
        self.main_window = main_window
        self.animation = animation
        self.animation_index = animation_index
        # Store full animation state
        self.animation_data = animation.to_dict()

    def redo(self):
        """Delete the animation"""
        if self.animation in self.main_window.project.animations:
            self.main_window.project.animations.remove(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()
        # Select another animation or none
        if len(self.main_window.project.animations) > 0:
            index = min(self.animation_index, len(self.main_window.project.animations) - 1)
            self.main_window.timeline_editor.animation_combo.setCurrentIndex(index)
            # Manually load since signals are blocked during refresh
            self.main_window.timeline_editor._load_animation(self.main_window.project.animations[index])
        else:
            self.main_window.timeline_editor._load_animation(None)

    def undo(self):
        """Restore the animation"""
        from telligram.core.animation import Animation
        restored_anim = Animation.from_dict(self.animation_data)
        self.main_window.project.animations.insert(self.animation_index, restored_anim)
        self.animation = restored_anim  # Update reference
        self.main_window.timeline_editor._refresh_animation_list()
        self.main_window.timeline_editor.animation_combo.setCurrentIndex(self.animation_index)
        # Manually load since signals are blocked during refresh
        self.main_window.timeline_editor._load_animation(restored_anim)


class AddFrameCommand(QUndoCommand):
    """Command for adding a frame to an animation"""

    def __init__(self, main_window, animation, card_slot, duration):
        super().__init__(f"Add Frame (Card #{card_slot})")
        self.main_window = main_window
        self.animation = animation
        self.card_slot = card_slot
        self.duration = duration
        self.frame_index = None

    def redo(self):
        """Add the frame"""
        self.animation.add_frame(self.card_slot, self.duration)
        self.frame_index = self.animation.frame_count - 1
        self.main_window.timeline_editor._load_animation(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()

    def undo(self):
        """Remove the frame"""
        if self.frame_index is not None and self.frame_index < self.animation.frame_count:
            self.animation.remove_frame(self.frame_index)
            self.main_window.timeline_editor._load_animation(self.animation)
            self.main_window.timeline_editor._refresh_animation_list()


class InsertFrameCommand(QUndoCommand):
    """Command for inserting a frame at a specific position"""

    def __init__(self, main_window, animation, index, card_slot, duration):
        super().__init__(f"Insert Frame at {index}")
        self.main_window = main_window
        self.animation = animation
        self.index = index
        self.card_slot = card_slot
        self.duration = duration

    def redo(self):
        """Insert the frame"""
        self.animation.insert_frame(self.index, self.card_slot, self.duration)
        self.main_window.timeline_editor._load_animation(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()

    def undo(self):
        """Remove the inserted frame"""
        if self.index < self.animation.frame_count:
            self.animation.remove_frame(self.index)
            self.main_window.timeline_editor._load_animation(self.animation)
            self.main_window.timeline_editor._refresh_animation_list()


class RemoveFrameCommand(QUndoCommand):
    """Command for removing a frame from an animation"""

    def __init__(self, main_window, animation, index):
        frame = animation.get_frame(index)
        super().__init__(f"Remove Card {index}")
        self.main_window = main_window
        self.animation = animation
        self.index = index
        self.card_slot = frame["card_slot"]
        self.duration = frame["duration"]

    def redo(self):
        """Remove the frame"""
        self.animation.remove_frame(self.index)
        self.main_window.timeline_editor._load_animation(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()

    def undo(self):
        """Restore the frame"""
        self.animation.insert_frame(self.index, self.card_slot, self.duration)
        self.main_window.timeline_editor._load_animation(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()


class ChangeFrameDurationCommand(QUndoCommand):
    """Command for changing a frame's duration"""

    def __init__(self, main_window, animation, frame_index, old_duration, new_duration):
        super().__init__(f"Change Card {frame_index} Duration")
        self.main_window = main_window
        self.animation = animation
        self.frame_index = frame_index
        self.old_duration = old_duration
        self.new_duration = new_duration

    def redo(self):
        """Apply new duration"""
        frame = self.animation.get_frame(self.frame_index)
        frame["duration"] = self.new_duration
        self.main_window.timeline_editor._refresh_animation_list()

    def undo(self):
        """Restore old duration"""
        frame = self.animation.get_frame(self.frame_index)
        frame["duration"] = self.old_duration
        self.main_window.timeline_editor._refresh_animation_list()


class ReorderFrameCommand(QUndoCommand):
    """Command for reordering a frame in the timeline"""

    def __init__(self, main_window, animation, from_index, to_index):
        super().__init__(f"Reorder Card {from_index} to {to_index}")
        self.main_window = main_window
        self.animation = animation
        self.from_index = from_index
        self.to_index = to_index

    def redo(self):
        """Reorder the frame"""
        if self.from_index != self.to_index:
            frame = self.animation._frames.pop(self.from_index)
            self.animation._frames.insert(self.to_index, frame)
            self.main_window.timeline_editor._load_animation(self.animation)

    def undo(self):
        """Reverse the reorder"""
        if self.from_index != self.to_index:
            frame = self.animation._frames.pop(self.to_index)
            self.animation._frames.insert(self.from_index, frame)
            self.main_window.timeline_editor._load_animation(self.animation)


class DuplicateFrameCommand(QUndoCommand):
    """Command for duplicating a frame"""

    def __init__(self, main_window, animation, index):
        frame = animation.get_frame(index)
        super().__init__(f"Duplicate Card {index}")
        self.main_window = main_window
        self.animation = animation
        self.index = index
        self.card_slot = frame["card_slot"]
        self.duration = frame["duration"]

    def redo(self):
        """Duplicate the frame"""
        self.animation.insert_frame(self.index + 1, self.card_slot, self.duration)
        self.main_window.timeline_editor._load_animation(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()

    def undo(self):
        """Remove the duplicated frame"""
        self.animation.remove_frame(self.index + 1)
        self.main_window.timeline_editor._load_animation(self.animation)
        self.main_window.timeline_editor._refresh_animation_list()
