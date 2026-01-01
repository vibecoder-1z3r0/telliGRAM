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
from telligram.gui.widgets.timeline_editor import TimelineEditorWidget


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.project = Project(name="Untitled")
        self.current_file = None
        self.current_card_slot = 0
        self.undo_stack = QUndoStack(self)

        self.setWindowTitle("telliGRAM - Intellivision GRAM Card Creator")
        self.setMinimumSize(1200, 800)

        self._create_menu_bar()
        self._create_widgets()
        self._create_status_bar()
        self._connect_signals()

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

        # Left panel - GRAM Card grid and pixel editor
        left_panel = QWidget()
        left_panel_layout = QHBoxLayout(left_panel)

        # GRAM Card grid
        grid_panel = QWidget()
        grid_layout = QVBoxLayout(grid_panel)
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

        self.card_label = QLabel("<h3>Card #0</h3>")
        editor_layout.addWidget(self.card_label)

        self.pixel_editor = PixelEditorWidget()
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
        editor_layout.addStretch()

        left_panel_layout.addWidget(editor_panel, stretch=2)

        main_layout.addWidget(left_panel, stretch=3)

        # Right panel - DISABLED for WSL debugging
        # TODO: Re-enable once WSL issues resolved
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("Right panel temporarily disabled for WSL debugging"))

        self.timeline_editor = None  # Disabled for now

        # self.tabs = QTabWidget()
        # self.tabs.currentChanged.connect(self._on_tab_changed)
        # self.timeline_editor = TimelineEditorWidget(self.project)
        # self.tabs.addTab(self.timeline_editor, "Animation Timeline")

        main_layout.addWidget(right_panel, stretch=1)

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
        # Timeline editor disabled for WSL debugging
        # self.timeline_editor.animation_changed.connect(self.on_animation_changed)

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
        if self.timeline_editor:  # Timeline editor disabled for now
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
                self.pixel_editor.set_card(self.project.get_card(self.current_card_slot))
                if self.timeline_editor:  # Timeline editor disabled for now
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
        if self.timeline_editor:  # Timeline editor disabled for now
            self.timeline_editor.set_current_card_slot(slot)

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
        card = self.pixel_editor.get_card()
        if card:
            card.flip_horizontal()
            self.pixel_editor.set_card(card)
            self.on_card_changed()

    def flip_vertical(self):
        """Flip current card vertically"""
        card = self.pixel_editor.get_card()
        if card:
            card.flip_vertical()
            self.pixel_editor.set_card(card)
            self.on_card_changed()

    def update_title(self):
        """Update window title"""
        title = "telliGRAM"
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
        # Animations are stored in the project, nothing special to do here
        # Just mark that the project has been modified (TODO: track dirty state)
        pass

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About telliGRAM",
            "<h2>telliGRAM v0.1.0</h2>"
            "<p>Intellivision GRAM Card Creator</p>"
            "<p>Create custom 8×8 graphics for Intellivision games</p>"
            "<p>© 2025 Vibe-Coder 1.z3r0</p>"
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

        # Perform the clear and store the result
        from telligram.core.card import GramCard
        card = main_window.project.get_card(slot)
        if card is not None:
            card.clear()
            self.new_data = card.to_bytes()


class FlipHorizontalCommand(CardOperationCommand):
    """Command for flipping a card horizontally"""

    def __init__(self, main_window, slot):
        super().__init__(main_window, slot, f"Flip Horizontal Card #{slot}")

        # Perform the flip and store the result
        from telligram.core.card import GramCard
        card = main_window.project.get_card(slot)
        if card is not None:
            card.flip_horizontal()
            self.new_data = card.to_bytes()


class FlipVerticalCommand(CardOperationCommand):
    """Command for flipping a card vertically"""

    def __init__(self, main_window, slot):
        super().__init__(main_window, slot, f"Flip Vertical Card #{slot}")

        # Perform the flip and store the result
        from telligram.core.card import GramCard
        card = main_window.project.get_card(slot)
        if card is not None:
            card.flip_vertical()
            self.new_data = card.to_bytes()


class PasteCardCommand(CardOperationCommand):
    """Command for pasting a card"""

    def __init__(self, main_window, slot, card_data):
        super().__init__(main_window, slot, f"Paste Card #{slot}")
        self.new_data = card_data
