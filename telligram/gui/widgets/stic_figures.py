"""
STIC Figures - Full-screen designer for Intellivision BACKTAB and MOB composition.

Allows visual design of complete Intellivision screens including:
- BACKTAB: 20×12 background tile grid (240 tiles)
- Color management: Color Stack mode
- Card placement from GRAM/GROM palettes
- Export to IntyBASIC/Assembly
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QPushButton, QComboBox, QCheckBox, QTabWidget, QGridLayout, QGroupBox,
    QSpinBox, QFileDialog, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QAction

from telligram.core.constants import get_color_hex, INTELLIVISION_PALETTE
from telligram.core.grom import GromData
from pathlib import Path
import json


def create_color_combo():
    """Create a QComboBox populated with Intellivision colors and visual swatches"""
    combo = QComboBox()
    for i, color_data in enumerate(INTELLIVISION_PALETTE):
        # Create color swatch pixmap
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(color_data["hex"]))

        # Add item with icon and text
        combo.addItem(
            pixmap,
            f"{i}: {color_data['name']}"
        )

    return combo


class ClickableContainer(QWidget):
    """Container widget that emits signal when clicked on empty space"""
    clicked = Signal()

    def mousePressEvent(self, event):
        """Emit clicked signal when background is clicked"""
        self.clicked.emit()
        super().mousePressEvent(event)


class BacktabCanvas(QWidget):
    """
    Canvas widget for displaying and editing the 20×12 BACKTAB grid.
    Each tile is 8×8 pixels, displayed at scale for editing.
    """

    tile_clicked = Signal(int, int)  # Emits (row, col) when clicked
    tile_ctrl_clicked = Signal(int, int)  # Emits (row, col) when Ctrl+clicked

    def __init__(self, parent=None):
        super().__init__(parent)

        # BACKTAB dimensions
        self.grid_cols = 20
        self.grid_rows = 12
        self.tile_size = 48  # Display size (8×8 pixels shown at 6× scale)

        # Canvas size with 8px border
        self.border_size = 48  # 8px border shown at 6× scale
        canvas_width = self.border_size * 2 + (self.grid_cols * self.tile_size)
        canvas_height = self.border_size * 2 + (self.grid_rows * self.tile_size)
        self.setFixedSize(canvas_width, canvas_height)

        # BACKTAB data: 240 tiles (row, col) -> tile_info
        self.backtab = {}
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                self.backtab[(row, col)] = {
                    'card': 0,  # Card number (0-319)
                    'fg_color': 7,  # Foreground color (0-15)
                    'advance_stack': False  # Advance color stack after tile
                }

        # Current color stack and position
        self.color_stack = [0, 1, 2, 3]  # Default: Black, Blue, Brown, Tan
        self.current_stack_pos = 0

        # Border settings
        self.border_visible = True
        self.border_color = 0  # Black
        self.show_left_border = True
        self.show_top_border = True

        # Display settings
        self.show_grid = True

        # Selection
        self.selected_row = None
        self.selected_col = None

        # Card data sources (set externally)
        self.grom_data = None
        self.gram_data = None

    def set_card_sources(self, grom_data, gram_data):
        """Set GROM and GRAM data sources"""
        self.grom_data = grom_data
        self.gram_data = gram_data
        self.update()

    def set_tile(self, row, col, card, fg_color, advance_stack=False):
        """Set tile data at specific position"""
        if (row, col) in self.backtab:
            self.backtab[(row, col)] = {
                'card': card,
                'fg_color': fg_color,
                'advance_stack': advance_stack
            }
            self.update()

    def get_tile(self, row, col):
        """Get tile data at specific position"""
        return self.backtab.get((row, col))

    def set_selected(self, row, col):
        """Set selected tile"""
        self.selected_row = row
        self.selected_col = col
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse clicks on canvas"""
        # Convert screen position to grid position
        x = event.position().x() - self.border_size
        y = event.position().y() - self.border_size

        if x >= 0 and y >= 0:
            col = int(x // self.tile_size)
            row = int(y // self.tile_size)

            if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                if event.button() == Qt.LeftButton:
                    # Check for Ctrl modifier
                    modifiers = event.modifiers()
                    if modifiers & Qt.ControlModifier:
                        # Ctrl+Click: paint current card
                        self.tile_ctrl_clicked.emit(row, col)
                    else:
                        # Normal click: select tile
                        self.tile_clicked.emit(row, col)
                    self.set_selected(row, col)

    def contextMenuEvent(self, event):
        """Handle right-click context menu"""
        # Convert screen position to grid position
        x = event.pos().x() - self.border_size
        y = event.pos().y() - self.border_size

        if x >= 0 and y >= 0:
            col = int(x // self.tile_size)
            row = int(y // self.tile_size)

            if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                # Create context menu
                menu = QMenu(self)
                clear_action = QAction("Set to GROM 0 (Blank)", self)
                clear_action.triggered.connect(lambda: self._clear_tile(row, col))
                menu.addAction(clear_action)

                # Show menu at cursor position
                menu.exec(event.globalPos())

    def _clear_tile(self, row, col):
        """Clear tile to GROM card 0 (blank)"""
        self.set_tile(row, col, card=0, fg_color=7, advance_stack=False)
        # Select the cleared tile to show it in properties
        self.set_selected(row, col)
        self.tile_clicked.emit(row, col)

    def paintEvent(self, event):
        """Render the BACKTAB canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Draw border
        if self.border_visible:
            border_hex = get_color_hex(self.border_color)
            painter.fillRect(0, 0, self.width(), self.height(), QColor(border_hex))

        # Draw BACKTAB playfield background
        playfield_x = self.border_size
        playfield_y = self.border_size
        playfield_w = self.grid_cols * self.tile_size
        playfield_h = self.grid_rows * self.tile_size

        # Calculate color stack position for each tile
        stack_pos = 0
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                tile = self.backtab[(row, col)]

                # Get background color from color stack
                bg_color_idx = self.color_stack[stack_pos % 4]
                bg_hex = get_color_hex(bg_color_idx)

                # Draw tile background
                tile_x = playfield_x + (col * self.tile_size)
                tile_y = playfield_y + (row * self.tile_size)
                painter.fillRect(tile_x, tile_y, self.tile_size, self.tile_size, QColor(bg_hex))

                # Draw tile foreground (card data)
                card_data = self._get_card_data(tile['card'])
                if card_data:
                    fg_hex = get_color_hex(tile['fg_color'])
                    self._draw_card(painter, tile_x, tile_y, card_data, fg_hex, bg_hex)

                # Advance stack if flag set
                if tile['advance_stack']:
                    stack_pos += 1

        # Draw grid lines
        if self.show_grid:
            painter.setPen(QPen(QColor("#555555"), 1))

            # Vertical lines
            for col in range(self.grid_cols + 1):
                x = playfield_x + (col * self.tile_size)
                painter.drawLine(x, playfield_y, x, playfield_y + playfield_h)

            # Horizontal lines
            for row in range(self.grid_rows + 1):
                y = playfield_y + (row * self.tile_size)
                painter.drawLine(playfield_x, y, playfield_x + playfield_w, y)

        # Draw selection highlight
        if self.selected_row is not None and self.selected_col is not None:
            sel_x = playfield_x + (self.selected_col * self.tile_size)
            sel_y = playfield_y + (self.selected_row * self.tile_size)
            painter.setPen(QPen(QColor("#FFD700"), 3))  # Gold/yellow
            painter.drawRect(sel_x, sel_y, self.tile_size, self.tile_size)

    def _get_card_data(self, card_num):
        """Get card bitmap data from GROM or GRAM"""
        if card_num < 256:
            # GROM card
            if self.grom_data:
                return self.grom_data.get_card(card_num)
        else:
            # GRAM card (256-319)
            if self.gram_data:
                gram_slot = card_num - 256
                if 0 <= gram_slot < len(self.gram_data):
                    return self.gram_data[gram_slot]
        return None

    def _draw_card(self, painter, x, y, card_data, fg_color, bg_color):
        """Draw an 8×8 card on the canvas"""
        if not card_data or len(card_data) != 8:
            return

        pixel_scale = self.tile_size // 8

        for row in range(8):
            byte = card_data[row]
            for col in range(8):
                bit = (byte >> (7 - col)) & 1
                if bit:  # Foreground pixel
                    px = x + (col * pixel_scale)
                    py = y + (row * pixel_scale)
                    painter.fillRect(px, py, pixel_scale, pixel_scale, QColor(fg_color))


class CardPaletteWidget(QWidget):
    """
    Card palette widget with GRAM and GROM tabs.
    Displays available cards for selection.
    """

    card_selected = Signal(int)  # Emits card number when selected
    card_deselected = Signal()  # Emits when clicking empty space

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("<h3>Card Palette</h3>")
        layout.addWidget(title)

        # Tab widget for GRAM/GROM
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # GRAM tab
        self.gram_scroll = QScrollArea()
        self.gram_scroll.setWidgetResizable(True)
        self.gram_container = ClickableContainer()
        self.gram_container.clicked.connect(lambda: self.card_deselected.emit())
        self.gram_layout = QVBoxLayout(self.gram_container)
        self.gram_layout.setAlignment(Qt.AlignTop)
        self.gram_scroll.setWidget(self.gram_container)
        self.tabs.addTab(self.gram_scroll, "GRAM")

        # GROM tab
        self.grom_scroll = QScrollArea()
        self.grom_scroll.setWidgetResizable(True)
        self.grom_container = ClickableContainer()
        self.grom_container.clicked.connect(lambda: self.card_deselected.emit())
        self.grom_layout = QVBoxLayout(self.grom_container)
        self.grom_layout.setAlignment(Qt.AlignTop)
        self.grom_scroll.setWidget(self.grom_container)
        self.tabs.addTab(self.grom_scroll, "GROM")

        # Selected card tracking
        self.selected_card = 0
        self.card_widgets = {}  # card_num -> widget

    def set_gram_data(self, gram_data):
        """Populate GRAM tab with project cards"""
        # Clear existing
        while self.gram_layout.count():
            child = self.gram_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add GRAM cards (256-319)
        for slot in range(64):
            if slot < len(gram_data):
                card_num = 256 + slot
                widget = self._create_card_thumbnail(card_num, gram_data[slot], f"GRAM Slot {slot}")
                self.gram_layout.addWidget(widget)
                self.card_widgets[card_num] = widget

    def set_grom_data(self, grom_data):
        """Populate GROM tab with GROM cards"""
        # Clear existing
        while self.grom_layout.count():
            child = self.grom_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add GROM cards (0-255)
        for card_num in range(256):
            card_data = grom_data.get_card(card_num)
            label = grom_data.get_label(card_num)
            widget = self._create_card_thumbnail(card_num, card_data, label)
            self.grom_layout.addWidget(widget)
            self.card_widgets[card_num] = widget

    def _create_card_thumbnail(self, card_num, card_data, label):
        """Create a clickable card thumbnail"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setFixedHeight(80)
        frame.setStyleSheet("QFrame { border: 1px solid #3c3c3c; background-color: #2b2b2b; }")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)

        # Card preview
        preview = QLabel()
        preview.setFixedSize(48, 48)
        pixmap = self._render_card_pixmap(card_data)
        preview.setPixmap(pixmap)
        layout.addWidget(preview)

        # Card info
        info_layout = QVBoxLayout()
        num_label = QLabel(f"#{card_num} (${card_num:03X})")
        info_layout.addWidget(num_label)

        if card_num >= 256:
            slot_label = QLabel(f"Slot {card_num - 256}")
            info_layout.addWidget(slot_label)

        if label:
            text_label = QLabel(label[:20])
            text_label.setStyleSheet("font-size: 10px; color: #888;")
            info_layout.addWidget(text_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Make clickable
        frame.mousePressEvent = lambda e: self._on_card_clicked(card_num, frame)
        frame.card_num = card_num

        return frame

    def _render_card_pixmap(self, card_data):
        """Render 8×8 card as QPixmap"""
        size = 48
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("#000000"))

        if card_data and len(card_data) == 8:
            painter = QPainter(pixmap)
            pixel_size = size // 8

            for row in range(8):
                byte = card_data[row]
                for col in range(8):
                    bit = (byte >> (7 - col)) & 1
                    if bit:
                        px = col * pixel_size
                        py = row * pixel_size
                        painter.fillRect(px, py, pixel_size, pixel_size, QColor("#FFFFFF"))
            painter.end()

        return pixmap

    def _on_card_clicked(self, card_num, frame):
        """Handle card selection"""
        # Update selection
        if self.selected_card in self.card_widgets:
            self.card_widgets[self.selected_card].setStyleSheet(
                "QFrame { border: 1px solid #3c3c3c; background-color: #2b2b2b; }"
            )

        self.selected_card = card_num
        frame.setStyleSheet("QFrame { border: 2px solid #0078D4; background-color: #1a3a52; }")
        self.card_selected.emit(card_num)


class SticFiguresWidget(QWidget):
    """Main STIC Figures widget with three-panel layout.

    Interaction Model:
    ------------------
    1. **Select from palette**: Click GRAM/GROM card to select it
       - Card becomes current_card for painting
       - Card selection persists even after clicking off palette

    2. **Click tile (Eyedropper)**: Click BACKTAB tile to inspect/copy it
       - Tile becomes selected, properties panel shows its values
       - current_card updates to match the tile's card (eyedropper)
       - Enables copying tiles: click source tile, Ctrl+Click targets

    3. **Ctrl+Click tile (Paint)**: Ctrl+Click to paint current_card
       - Immediately paints current_card to clicked tile
       - Works with cards from palette OR from eyedropper
       - Brush workflow: select once, Ctrl+Click multiple tiles

    4. **Right-click tile (Clear)**: Right-click → "Set to GROM 0"
       - Quickly clears tile to blank card
       - Useful for erasing or resetting tiles

    5. **Properties panel**: Modify selected tile's card/colors/flags
       - Changes apply immediately to selected tile
       - Spinbox, color combos, checkboxes all update live
    """

    def __init__(self, project=None, grom_path=None, parent=None):
        super().__init__(parent)

        self.project = project
        self.main_window = None  # Set by main_window after creation
        self.current_figure = None  # Current STIC figure being edited
        self.grom_data = None

        # Load GROM if provided
        if grom_path:
            self.grom_data = GromData(grom_path)

        # Main layout: three panels
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Left panel: Card Palette (240px)
        self.palette_widget = CardPaletteWidget()
        self.palette_widget.setFixedWidth(240)
        self.palette_widget.card_selected.connect(self._on_card_selected)
        self.palette_widget.card_deselected.connect(self._on_card_deselected)
        main_layout.addWidget(self.palette_widget)

        # Center panel: BACKTAB Canvas
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setAlignment(Qt.AlignCenter)

        canvas_title = QLabel("<h3>BACKTAB Canvas (20×12)</h3>")
        canvas_title.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(canvas_title)

        self.canvas = BacktabCanvas()
        self.canvas.tile_clicked.connect(self._on_tile_clicked)
        self.canvas.tile_ctrl_clicked.connect(self._on_tile_ctrl_clicked)
        center_layout.addWidget(self.canvas, alignment=Qt.AlignCenter)

        center_layout.addStretch()
        main_layout.addWidget(center_panel, stretch=1)

        # Right panel: Properties (280px)
        right_panel = QWidget()
        right_panel.setFixedWidth(280)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignTop)

        props_title = QLabel("<h3>Properties</h3>")
        right_layout.addWidget(props_title)

        # Display settings group
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)

        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.toggled.connect(self._on_grid_toggled)
        display_layout.addWidget(self.grid_checkbox)

        self.border_checkbox = QCheckBox("Show Border")
        self.border_checkbox.setChecked(True)
        self.border_checkbox.toggled.connect(self._on_border_toggled)
        display_layout.addWidget(self.border_checkbox)

        # Border color
        border_color_layout = QHBoxLayout()
        border_color_layout.addWidget(QLabel("Border Color:"))
        self.border_color_combo = create_color_combo()
        self.border_color_combo.setCurrentIndex(0)  # Black
        self.border_color_combo.currentIndexChanged.connect(self._on_border_color_changed)
        border_color_layout.addWidget(self.border_color_combo)
        display_layout.addLayout(border_color_layout)

        right_layout.addWidget(display_group)

        # Selected tile group
        tile_group = QGroupBox("Selected Tile")
        tile_layout = QVBoxLayout(tile_group)

        self.tile_info_label = QLabel("No tile selected")
        tile_layout.addWidget(self.tile_info_label)

        # Card number display
        card_layout = QHBoxLayout()
        card_layout.addWidget(QLabel("Card:"))
        self.card_spin = QSpinBox()
        self.card_spin.setRange(0, 319)
        self.card_spin.setValue(0)
        self.card_spin.valueChanged.connect(self._on_card_changed)
        card_layout.addWidget(self.card_spin)
        tile_layout.addLayout(card_layout)

        # Foreground color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("FG Color:"))
        self.fg_color_combo = create_color_combo()
        self.fg_color_combo.setCurrentIndex(7)  # White
        self.fg_color_combo.currentIndexChanged.connect(self._on_fg_color_changed)
        color_layout.addWidget(self.fg_color_combo)
        tile_layout.addLayout(color_layout)

        # Advance stack checkbox
        self.advance_stack_checkbox = QCheckBox("Advance Color Stack")
        self.advance_stack_checkbox.toggled.connect(self._on_advance_stack_toggled)
        tile_layout.addWidget(self.advance_stack_checkbox)

        right_layout.addWidget(tile_group)

        # Color stack group
        stack_group = QGroupBox("Color Stack")
        stack_layout = QVBoxLayout(stack_group)

        self.stack_combos = []
        for i in range(4):
            slot_layout = QHBoxLayout()
            slot_layout.addWidget(QLabel(f"Slot {i}:"))
            combo = create_color_combo()
            combo.setCurrentIndex([0, 1, 2, 3][i])  # Default stack
            combo.currentIndexChanged.connect(lambda idx, slot=i: self._on_stack_color_changed(slot, idx))
            slot_layout.addWidget(combo)
            stack_layout.addLayout(slot_layout)
            self.stack_combos.append(combo)

        right_layout.addWidget(stack_group)

        # Figure management
        figure_group = QGroupBox("STIC Figure")
        figure_layout = QVBoxLayout(figure_group)

        # Figure dropdown
        self.figure_combo = QComboBox()
        self.figure_combo.setMinimumWidth(200)
        self.figure_combo.currentIndexChanged.connect(self._on_figure_selected)
        figure_layout.addWidget(self.figure_combo)

        # Figure management buttons
        button_layout1 = QHBoxLayout()
        self.new_figure_btn = QPushButton("New")
        self.new_figure_btn.clicked.connect(self._new_figure)
        button_layout1.addWidget(self.new_figure_btn)

        self.rename_figure_btn = QPushButton("Rename")
        self.rename_figure_btn.clicked.connect(self._rename_figure)
        button_layout1.addWidget(self.rename_figure_btn)

        self.delete_figure_btn = QPushButton("Delete")
        self.delete_figure_btn.clicked.connect(self._delete_figure)
        button_layout1.addWidget(self.delete_figure_btn)
        figure_layout.addLayout(button_layout1)

        # Import/Export buttons (placeholders for now)
        button_layout2 = QHBoxLayout()
        self.import_figure_btn = QPushButton("Import...")
        self.import_figure_btn.clicked.connect(self._import_figure)
        button_layout2.addWidget(self.import_figure_btn)

        self.export_figure_btn = QPushButton("Export...")
        self.export_figure_btn.clicked.connect(self._export_figure)
        button_layout2.addWidget(self.export_figure_btn)
        figure_layout.addLayout(button_layout2)

        right_layout.addWidget(figure_group)
        right_layout.addStretch()

        main_layout.addWidget(right_panel)

        # Initialize data
        self._update_palette()
        self._update_canvas_data()
        self._refresh_figure_list()

        # Current selection state
        self.current_card = 0
        self.current_fg_color = 7
        self.selected_row = None
        self.selected_col = None

    def showEvent(self, event):
        """Refresh palette when tab becomes visible"""
        super().showEvent(event)
        # Refresh GRAM palette to show any cards created/edited in other tabs
        self._update_palette()
        self._update_canvas_data()

    def set_project(self, project):
        """Update project reference (called when project is loaded/changed)"""
        self.project = project
        self._update_palette()
        self._update_canvas_data()
        self._refresh_figure_list()
        # Load first figure if available
        if len(self.project.stic_figures) > 0:
            self.figure_combo.setCurrentIndex(0)

    def _update_palette(self):
        """Update card palette with GRAM/GROM data"""
        if self.project:
            gram_data = []
            for i in range(64):
                card = self.project.get_card(i)
                if card is not None:
                    gram_data.append(card.to_bytes())
                else:
                    gram_data.append([0] * 8)  # Empty card
            self.palette_widget.set_gram_data(gram_data)

        if self.grom_data:
            self.palette_widget.set_grom_data(self.grom_data)

    def _update_canvas_data(self):
        """Update canvas with GRAM/GROM data sources"""
        if self.project and self.grom_data:
            gram_data = []
            for i in range(64):
                card = self.project.get_card(i)
                if card is not None:
                    gram_data.append(card.to_bytes())
                else:
                    gram_data.append([0] * 8)  # Empty card
            self.canvas.set_card_sources(self.grom_data, gram_data)

    def _on_card_selected(self, card_num):
        """Handle card selection from palette"""
        self.current_card = card_num

        # Only paint if a tile is already selected
        # This prevents accidental painting when clicking card first
        if self.selected_row is not None and self.selected_col is not None:
            self._apply_current_to_selected()
            # Update UI to show what was just painted
            self._update_properties_from_tile(self.selected_row, self.selected_col)

    def _on_card_deselected(self):
        """Handle card deselection (clicking empty palette area)"""
        # Keep current card for Ctrl+Click painting
        # Visual deselection in palette is enough feedback
        pass

    def _update_properties_from_tile(self, row, col):
        """Update properties panel to show tile's current state"""
        tile = self.canvas.get_tile(row, col)
        if tile:
            self.tile_info_label.setText(f"Row: {row}, Col: {col}")

            self.card_spin.blockSignals(True)
            self.card_spin.setValue(tile['card'])
            self.card_spin.blockSignals(False)

            self.fg_color_combo.blockSignals(True)
            self.fg_color_combo.setCurrentIndex(tile['fg_color'])
            self.fg_color_combo.blockSignals(False)

            self.advance_stack_checkbox.blockSignals(True)
            self.advance_stack_checkbox.setChecked(tile['advance_stack'])
            self.advance_stack_checkbox.blockSignals(False)

            # Update current card/color to match tile (eyedropper effect)
            self.current_card = tile['card']
            self.current_fg_color = tile['fg_color']

    def _on_tile_clicked(self, row, col):
        """Handle tile click on canvas - selects tile with eyedropper effect.

        Updates current_card to match the clicked tile, allowing you to:
        1. Click a palette card, then click tiles to select them (normal flow)
        2. Click a tile to "pick up" its card, then Ctrl+Click other tiles to copy it
        """
        self.selected_row = row
        self.selected_col = col

        # Update properties panel to show tile's current state
        # This also updates current_card (eyedropper effect)
        self._update_properties_from_tile(row, col)

    def _on_tile_ctrl_clicked(self, row, col):
        """Handle Ctrl+Click on tile - paint current card.

        Paints whatever card is currently selected (either from palette or
        from clicking another tile). This enables a "brush" workflow for
        quickly painting multiple tiles with the same card.
        """
        self.selected_row = row
        self.selected_col = col

        # Paint the current card immediately
        self._apply_current_to_selected()

        # Update properties panel to show what was just painted
        self._update_properties_from_tile(row, col)

    def _apply_current_to_selected(self):
        """Apply current card and color to selected tile"""
        if self.selected_row is not None and self.selected_col is not None:
            # Update canvas
            self.canvas.set_tile(
                self.selected_row,
                self.selected_col,
                self.current_card,
                self.current_fg_color,
                self.advance_stack_checkbox.isChecked()
            )
            # Update current figure if one is loaded
            if self.current_figure:
                self.current_figure.set_tile(
                    self.selected_row,
                    self.selected_col,
                    self.current_card,
                    self.current_fg_color,
                    advance_stack=self.advance_stack_checkbox.isChecked()
                )

    def _on_card_changed(self, value):
        """Handle card number change"""
        self.current_card = value
        if self.selected_row is not None and self.selected_col is not None:
            self._apply_current_to_selected()

    def _on_fg_color_changed(self, index):
        """Handle foreground color change"""
        self.current_fg_color = index
        if self.selected_row is not None and self.selected_col is not None:
            self._apply_current_to_selected()

    def _on_advance_stack_toggled(self, checked):
        """Handle advance stack checkbox toggle"""
        if self.selected_row is not None and self.selected_col is not None:
            self._apply_current_to_selected()

    def _on_grid_toggled(self, checked):
        """Handle grid visibility toggle"""
        self.canvas.show_grid = checked
        self.canvas.update()

    def _on_border_toggled(self, checked):
        """Handle border visibility toggle"""
        self.canvas.border_visible = checked
        if self.current_figure:
            self.current_figure.border_visible = checked
        self.canvas.update()

    def _on_border_color_changed(self, color_idx):
        """Handle border color change"""
        self.canvas.border_color = color_idx
        if self.current_figure:
            self.current_figure.border_color = color_idx
        self.canvas.update()

    def _on_stack_color_changed(self, slot, color_idx):
        """Handle color stack change"""
        self.canvas.color_stack[slot] = color_idx
        if self.current_figure:
            self.current_figure.color_stack[slot] = color_idx
        self.canvas.update()

    def _refresh_figure_list(self):
        """Refresh figure dropdown from project"""
        if not self.project:
            return

        # Block signals to prevent triggering selection changes
        self.figure_combo.blockSignals(True)
        self.figure_combo.clear()

        # Add all figures from project
        for figure in self.project.stic_figures:
            self.figure_combo.addItem(figure.name)

        self.figure_combo.blockSignals(False)

        # Enable/disable buttons based on figure availability
        has_figures = len(self.project.stic_figures) > 0
        self.rename_figure_btn.setEnabled(has_figures)
        self.delete_figure_btn.setEnabled(has_figures)
        self.export_figure_btn.setEnabled(has_figures)

    def _on_figure_selected(self, index):
        """Handle figure selection from dropdown"""
        if not self.project or index < 0:
            self.current_figure = None
            return

        if index < len(self.project.stic_figures):
            self.current_figure = self.project.stic_figures[index]
            self._load_figure(self.current_figure)

    def _load_figure(self, figure):
        """Load a figure into the canvas and UI"""
        if not figure:
            return

        # Update canvas border settings
        self.canvas.border_visible = figure.border_visible
        self.canvas.border_color = figure.border_color
        self.canvas.show_left_border = figure.show_left_border
        self.canvas.show_top_border = figure.show_top_border

        # Update border UI
        self.border_checkbox.setChecked(figure.border_visible)
        self.border_color_combo.setCurrentIndex(figure.border_color)

        # Update color stack
        self.canvas.color_stack = figure.color_stack.copy()
        for i in range(4):
            if i < len(figure.color_stack):
                self.stack_combos[i].setCurrentIndex(figure.color_stack[i])

        # Load BACKTAB tiles
        for tile_data in figure.get_all_tiles():
            row = tile_data["row"]
            col = tile_data["col"]
            self.canvas.set_tile(
                row, col,
                tile_data["card"],
                tile_data["fg_color"],
                tile_data.get("advance_stack", False)
            )

        self.canvas.update()

    def _new_figure(self):
        """Create new STIC figure"""
        if not self.project:
            return

        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New STIC Figure", "Figure name:")
        if not ok or not name:
            return

        # Create new figure
        from telligram.core.stic_figure import SticFigure
        figure = SticFigure(name=name)
        self.project.add_stic_figure(figure)
        self._refresh_figure_list()
        # Select the newly created figure
        self.figure_combo.setCurrentIndex(len(self.project.stic_figures) - 1)

    def _rename_figure(self):
        """Rename current STIC figure"""
        if not self.current_figure:
            return

        from PySide6.QtWidgets import QInputDialog
        old_name = self.current_figure.name
        name, ok = QInputDialog.getText(self, "Rename STIC Figure", "New name:", text=old_name)
        if ok and name and name != old_name:
            self.current_figure.name = name
            self._refresh_figure_list()

    def _delete_figure(self):
        """Delete current STIC figure"""
        if not self.current_figure or not self.project:
            return

        reply = QMessageBox.question(
            self,
            "Delete STIC Figure",
            f"Delete figure '{self.current_figure.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Find current index before deletion
            current_index = self.project.stic_figures.index(self.current_figure)
            self.project.stic_figures.remove(self.current_figure)
            self._refresh_figure_list()
            # Select another figure or none
            if len(self.project.stic_figures) > 0:
                index = min(current_index, len(self.project.stic_figures) - 1)
                self.figure_combo.setCurrentIndex(index)
            else:
                self.current_figure = None

    def _import_figure(self):
        """Import STIC figure from .sticfig file (placeholder)"""
        QMessageBox.information(
            self,
            "Import Figure",
            "Import functionality will be implemented in a future update."
        )

    def _export_figure(self):
        """Export current STIC figure (placeholder)"""
        QMessageBox.information(
            self,
            "Export Figure",
            "Export functionality will be implemented in a future update."
        )

    def save_figure(self):
        """Save current STIC Figure to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save STIC Figure",
            "",
            "STIC Figure Files (*.sticfig);;JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Build BACKTAB data array
            backtab_data = []
            for row in range(self.canvas.grid_rows):
                for col in range(self.canvas.grid_cols):
                    tile = self.canvas.get_tile(row, col)
                    backtab_data.append({
                        "row": row,
                        "col": col,
                        "card": tile['card'],
                        "fg_color": tile['fg_color'],
                        "advance_stack": tile['advance_stack']
                    })

            # Build complete figure data
            figure_data = {
                "name": Path(file_path).stem,
                "mode": "color_stack",  # Phase 1 only supports Color Stack mode
                "border": {
                    "visible": self.canvas.border_visible,
                    "color": self.canvas.border_color,
                    "show_left": self.canvas.show_left_border,
                    "show_top": self.canvas.show_top_border
                },
                "color_stack": self.canvas.color_stack.copy(),
                "backtab": backtab_data
            }

            # Save to file
            with open(file_path, 'w') as f:
                json.dump(figure_data, f, indent=2)

            QMessageBox.information(
                self,
                "Success",
                f"STIC Figure saved to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save STIC Figure:\n{str(e)}"
            )

    def load_figure(self):
        """Load STIC Figure from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load STIC Figure",
            "",
            "STIC Figure Files (*.sticfig);;JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Load from file
            with open(file_path, 'r') as f:
                figure_data = json.load(f)

            # Validate data
            if "backtab" not in figure_data:
                raise ValueError("Invalid STIC Figure file: missing 'backtab' field")

            # Load border settings
            if "border" in figure_data:
                border = figure_data["border"]
                self.canvas.border_visible = border.get("visible", True)
                self.canvas.border_color = border.get("color", 0)
                self.canvas.show_left_border = border.get("show_left", True)
                self.canvas.show_top_border = border.get("show_top", True)

                # Update UI
                self.border_checkbox.setChecked(self.canvas.border_visible)

            # Load color stack
            if "color_stack" in figure_data:
                self.canvas.color_stack = figure_data["color_stack"].copy()

                # Update UI
                for i in range(4):
                    if i < len(self.canvas.color_stack):
                        self.stack_combos[i].setCurrentIndex(self.canvas.color_stack[i])

            # Load BACKTAB data
            for tile_data in figure_data["backtab"]:
                row = tile_data["row"]
                col = tile_data["col"]
                card = tile_data["card"]
                fg_color = tile_data["fg_color"]
                advance_stack = tile_data.get("advance_stack", False)

                self.canvas.set_tile(row, col, card, fg_color, advance_stack)

            # Refresh canvas
            self.canvas.update()

            QMessageBox.information(
                self,
                "Success",
                f"STIC Figure loaded from:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load STIC Figure:\n{str(e)}"
            )
