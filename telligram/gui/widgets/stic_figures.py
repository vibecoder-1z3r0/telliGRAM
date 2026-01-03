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
    QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap

from telligram.core.constants import get_color_hex
from telligram.core.grom import GromData
import json


class BacktabCanvas(QWidget):
    """
    Canvas widget for displaying and editing the 20×12 BACKTAB grid.
    Each tile is 8×8 pixels, displayed at scale for editing.
    """

    tile_clicked = Signal(int, int)  # Emits (row, col) when clicked

    def __init__(self, parent=None):
        super().__init__(parent)

        # BACKTAB dimensions
        self.grid_cols = 20
        self.grid_rows = 12
        self.tile_size = 24  # Display size (8×8 pixels shown at 3× scale)

        # Canvas size with 8px border
        self.border_size = 24  # 8px border shown at 3× scale
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
        if event.button() == Qt.LeftButton:
            # Convert screen position to grid position
            x = event.position().x() - self.border_size
            y = event.position().y() - self.border_size

            if x >= 0 and y >= 0:
                col = int(x // self.tile_size)
                row = int(y // self.tile_size)

                if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                    self.tile_clicked.emit(row, col)
                    self.set_selected(row, col)

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
        self.gram_container = QWidget()
        self.gram_layout = QVBoxLayout(self.gram_container)
        self.gram_layout.setAlignment(Qt.AlignTop)
        self.gram_scroll.setWidget(self.gram_container)
        self.tabs.addTab(self.gram_scroll, "GRAM")

        # GROM tab
        self.grom_scroll = QScrollArea()
        self.grom_scroll.setWidgetResizable(True)
        self.grom_container = QWidget()
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
    """Main STIC Figures widget with three-panel layout"""

    def __init__(self, project=None, grom_path=None, parent=None):
        super().__init__(parent)

        self.project = project
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
        self.fg_color_combo = QComboBox()
        for i in range(16):
            self.fg_color_combo.addItem(f"Color {i}")
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
            combo = QComboBox()
            for c in range(16):
                combo.addItem(f"Color {c}")
            combo.setCurrentIndex([0, 1, 2, 3][i])  # Default stack
            combo.currentIndexChanged.connect(lambda idx, slot=i: self._on_stack_color_changed(slot, idx))
            slot_layout.addWidget(combo)
            stack_layout.addLayout(slot_layout)
            self.stack_combos.append(combo)

        right_layout.addWidget(stack_group)
        right_layout.addStretch()

        main_layout.addWidget(right_panel)

        # Initialize data
        self._update_palette()
        self._update_canvas_data()

        # Current selection state
        self.current_card = 0
        self.current_fg_color = 7
        self.selected_row = None
        self.selected_col = None

    def _update_palette(self):
        """Update card palette with GRAM/GROM data"""
        if self.project:
            gram_data = [self.project.get_card_data(i) for i in range(64)]
            self.palette_widget.set_gram_data(gram_data)

        if self.grom_data:
            self.palette_widget.set_grom_data(self.grom_data)

    def _update_canvas_data(self):
        """Update canvas with GRAM/GROM data sources"""
        if self.project and self.grom_data:
            gram_data = [self.project.get_card_data(i) for i in range(64)]
            self.canvas.set_card_sources(self.grom_data, gram_data)

    def _on_card_selected(self, card_num):
        """Handle card selection from palette"""
        self.current_card = card_num
        self.card_spin.setValue(card_num)

        # If tile is selected, apply to it
        if self.selected_row is not None and self.selected_col is not None:
            self._apply_current_to_selected()

    def _on_tile_clicked(self, row, col):
        """Handle tile click on canvas"""
        self.selected_row = row
        self.selected_col = col

        # Update properties panel
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

        # Apply current card/color to clicked tile
        self._apply_current_to_selected()

    def _apply_current_to_selected(self):
        """Apply current card and color to selected tile"""
        if self.selected_row is not None and self.selected_col is not None:
            self.canvas.set_tile(
                self.selected_row,
                self.selected_col,
                self.current_card,
                self.current_fg_color,
                self.advance_stack_checkbox.isChecked()
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
        self.canvas.update()

    def _on_stack_color_changed(self, slot, color_idx):
        """Handle color stack change"""
        self.canvas.color_stack[slot] = color_idx
        self.canvas.update()
