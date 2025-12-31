"""Main application window for telliGRAM"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QFileDialog, QMessageBox, QStatusBar,
    QLabel, QPushButton, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
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

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

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

        self.card_grid = CardGridWidget()
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

        # Right panel - Tabbed view for GROM browser and Timeline editor
        self.tabs = QTabWidget()

        # GROM Browser tab
        self.grom_browser = GromBrowserWidget()
        self.tabs.addTab(self.grom_browser, "GROM Browser")

        # Timeline Editor tab
        self.timeline_editor = TimelineEditorWidget(self.project)
        self.tabs.addTab(self.timeline_editor, "Animation Timeline")

        main_layout.addWidget(self.tabs, stretch=1)

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self):
        """Connect widget signals"""
        self.card_grid.card_selected.connect(self.on_card_selected)
        self.pixel_editor.card_changed.connect(self.on_card_changed)
        self.timeline_editor.animation_changed.connect(self.on_animation_changed)

    def new_project(self):
        """Create new project"""
        # TODO: Ask to save current project if modified
        self.project = Project(name="Untitled")
        self.current_file = None
        self.card_grid.set_project(self.project)
        self.pixel_editor.set_card(None)
        self.timeline_editor.set_project(self.project)
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
                self.timeline_editor.set_project(self.project)
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
        self.pixel_editor.clear_card()

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
