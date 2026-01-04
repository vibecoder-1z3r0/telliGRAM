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
    QSpinBox, QFileDialog, QMessageBox, QMenu, QRadioButton, QButtonGroup
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
                    'bg_color': 0,  # Background color (0-15, FG/BG mode only)
                    'advance_stack': False  # Advance color stack after tile
                }

        # MOB data: 8 MOBs
        self.mobs = []
        for i in range(8):
            self.mobs.append({
                "visible": False,
                "card": 256,
                "x": 0,
                "y": 0,
                "color": 7,
                "priority": False,
                "size": 0,
                "h_flip": False,
                "v_flip": False
            })

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
        self.display_mode = "color_stack"  # or "fg_bg"
        self.show_hover_info = False  # Start disabled

        # Selection
        self.selected_row = None
        self.selected_col = None

        # Hover tracking for on-canvas display
        self.hovered_row = None
        self.hovered_col = None

        # Card data sources (set externally)
        self.grom_data = None
        self.gram_data = None

        # Enable mouse tracking for hover display
        self.setMouseTracking(True)

    def set_card_sources(self, grom_data, gram_data):
        """Set GROM and GRAM data sources"""
        self.grom_data = grom_data
        self.gram_data = gram_data
        self.update()

    def set_tile(self, row, col, card, fg_color, bg_color=0, advance_stack=False):
        """Set tile data at specific position"""
        if (row, col) in self.backtab:
            self.backtab[(row, col)] = {
                'card': card,
                'fg_color': fg_color,
                'bg_color': bg_color,
                'advance_stack': advance_stack
            }
            self.update()

    def get_tile(self, row, col):
        """Get tile data at specific position"""
        return self.backtab.get((row, col))

    def clear_all_tiles(self):
        """Reset all tiles to default (blank) state"""
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                self.backtab[(row, col)] = {
                    'card': 0,
                    'fg_color': 7,
                    'bg_color': 0,
                    'advance_stack': False
                }
        self.update()

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

    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover display"""
        # Convert screen position to grid position
        x = event.position().x() - self.border_size
        y = event.position().y() - self.border_size

        prev_row = self.hovered_row
        prev_col = self.hovered_col

        if x >= 0 and y >= 0:
            col = int(x // self.tile_size)
            row = int(y // self.tile_size)

            if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                self.hovered_row = row
                self.hovered_col = col
            else:
                self.hovered_row = None
                self.hovered_col = None
        else:
            self.hovered_row = None
            self.hovered_col = None

        # Repaint if hover changed
        if (self.hovered_row != prev_row or self.hovered_col != prev_col):
            self.update()

    def leaveEvent(self, event):
        """Clear hover when mouse leaves canvas"""
        if self.hovered_row is not None or self.hovered_col is not None:
            self.hovered_row = None
            self.hovered_col = None
            self.update()

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

        # Render tiles based on display mode
        # STEP 1: Draw all tile backgrounds
        if self.display_mode == "color_stack":
            # Color Stack mode: simulate color stack with advance_stack flags
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

                    # Advance stack if flag set
                    if tile['advance_stack']:
                        stack_pos += 1

        else:  # fg_bg mode
            # FG/BG mode: use tile's fg_color and bg_color directly
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    tile = self.backtab[(row, col)]

                    # Get background color
                    bg_color_idx = tile.get('bg_color', 0)
                    bg_hex = get_color_hex(bg_color_idx)

                    # Draw tile background
                    tile_x = playfield_x + (col * self.tile_size)
                    tile_y = playfield_y + (row * self.tile_size)
                    painter.fillRect(tile_x, tile_y, self.tile_size, self.tile_size, QColor(bg_hex))

        # STEP 2: Draw MOBs with priority=False (behind foreground)
        self._draw_mobs(painter, priority=False)

        # STEP 3: Draw all tile foregrounds (card data)
        if self.display_mode == "color_stack":
            stack_pos = 0
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    tile = self.backtab[(row, col)]

                    # Get colors
                    bg_color_idx = self.color_stack[stack_pos % 4]
                    fg_hex = get_color_hex(tile['fg_color'])
                    bg_hex = get_color_hex(bg_color_idx)

                    # Draw tile foreground (card data)
                    tile_x = playfield_x + (col * self.tile_size)
                    tile_y = playfield_y + (row * self.tile_size)
                    card_data = self._get_card_data(tile['card'])
                    if card_data:
                        self._draw_card(painter, tile_x, tile_y, card_data, fg_hex, bg_hex)

                    # Advance stack if flag set
                    if tile['advance_stack']:
                        stack_pos += 1

        else:  # fg_bg mode
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    tile = self.backtab[(row, col)]

                    # Get colors
                    fg_color_idx = tile['fg_color']
                    bg_color_idx = tile.get('bg_color', 0)
                    fg_hex = get_color_hex(fg_color_idx)
                    bg_hex = get_color_hex(bg_color_idx)

                    # Draw tile foreground (card data)
                    tile_x = playfield_x + (col * self.tile_size)
                    tile_y = playfield_y + (row * self.tile_size)
                    card_data = self._get_card_data(tile['card'])
                    if card_data:
                        self._draw_card(painter, tile_x, tile_y, card_data, fg_hex, bg_hex)

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

        # Draw hover info on tile (if enabled)
        if self.show_hover_info and self.hovered_row is not None and self.hovered_col is not None:
            hover_x = playfield_x + (self.hovered_col * self.tile_size)
            hover_y = playfield_y + (self.hovered_row * self.tile_size)

            # Calculate BACKTAB card number
            backtab_card = self.hovered_row * 20 + self.hovered_col

            # Draw semi-transparent background
            painter.fillRect(hover_x, hover_y, self.tile_size, self.tile_size,
                           QColor(0, 0, 0, 180))

            # Draw text
            painter.setPen(QColor("#FFFFFF"))
            from PySide6.QtGui import QFont
            font = QFont("Monospace", 7)
            painter.setFont(font)

            # Line 1: Card number
            painter.drawText(hover_x + 2, hover_y + 10, f"#: {backtab_card}")
            # Line 2: Row, Col
            painter.drawText(hover_x + 2, hover_y + 20, f"R:{self.hovered_row}")
            painter.drawText(hover_x + 2, hover_y + 30, f"C:{self.hovered_col}")

        # STEP 4: Draw MOBs with priority=True (in front of foreground)
        self._draw_mobs(painter, priority=True)

    def _draw_mobs(self, painter, priority):
        """Draw MOBs with the specified priority setting"""
        for mob_idx, mob in enumerate(self.mobs):
            # Only draw MOBs matching the requested priority
            if not mob['visible'] or mob['priority'] != priority:
                continue

            # Get card data (MOBs can only use GRAM cards 256-319)
            card_data = self._get_card_data(mob['card'])
            if not card_data:
                continue

            # Calculate MOB canvas position from world coordinates
            # World coords are in INTV pixels (0-175, 0-111), scale by 6 for canvas
            mob_x = mob['x'] * 6
            mob_y = mob['y'] * 6

            # Get size multiplier (0=8x8, 1=8x16, 2=16x8, 3=16x16)
            size_map = {
                0: (1, 1),   # 8x8
                1: (1, 2),   # 8x16
                2: (2, 1),   # 16x8
                3: (2, 2)    # 16x16
            }
            width_mult, height_mult = size_map.get(mob['size'], (1, 1))

            # Get color
            fg_hex = get_color_hex(mob['color'])

            # Draw the MOB card (with size and flip)
            self._draw_mob_card(
                painter, mob_x, mob_y, card_data,
                fg_hex, width_mult, height_mult,
                mob['h_flip'], mob['v_flip']
            )

    def _draw_mob_card(self, painter, x, y, card_data, fg_hex, width_mult, height_mult, h_flip, v_flip):
        """Draw a MOB card at the specified position with size and flip"""
        # MOBs are transparent (no background), so we just draw the foreground pixels
        pixel_scale = 6  # Each card pixel is 6x6 display pixels

        for row_idx, row_byte in enumerate(card_data):
            for bit in range(8):
                if row_byte & (1 << (7 - bit)):
                    # Calculate pixel position
                    pixel_col = bit
                    pixel_row = row_idx

                    # Apply horizontal flip
                    if h_flip:
                        pixel_col = 7 - pixel_col

                    # Apply vertical flip
                    if v_flip:
                        pixel_row = 7 - pixel_row

                    # Calculate display position with size multiplier
                    px = x + (pixel_col * pixel_scale * width_mult)
                    py = y + (pixel_row * pixel_scale * height_mult)

                    # Draw the pixel(s) based on size
                    pixel_width = pixel_scale * width_mult
                    pixel_height = pixel_scale * height_mult
                    painter.fillRect(px, py, pixel_width, pixel_height, QColor(fg_hex))

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

        # Center panel: STIC Figure Management + BACKTAB Canvas
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setAlignment(Qt.AlignTop)

        # BACKTAB Canvas (at top)
        canvas_title = QLabel("<h3>BACKTAB Canvas (20×12)</h3>")
        canvas_title.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(canvas_title)

        self.canvas = BacktabCanvas()
        self.canvas.tile_clicked.connect(self._on_tile_clicked)
        self.canvas.tile_ctrl_clicked.connect(self._on_tile_ctrl_clicked)
        center_layout.addWidget(self.canvas, alignment=Qt.AlignCenter)

        # STIC Figure management (below canvas)
        figures_label = QLabel("<b>Figures</b>")
        center_layout.addWidget(figures_label)

        figure_group = QGroupBox()  # Grey box
        figure_layout = QHBoxLayout(figure_group)

        # Figure dropdown (bigger)
        self.figure_combo = QComboBox()
        self.figure_combo.setMinimumWidth(350)
        self.figure_combo.currentIndexChanged.connect(self._on_figure_selected)
        figure_layout.addWidget(self.figure_combo)

        # All buttons in one row (smaller)
        self.new_figure_btn = QPushButton("New")
        self.new_figure_btn.setMaximumWidth(80)
        self.new_figure_btn.clicked.connect(self._new_figure)
        figure_layout.addWidget(self.new_figure_btn)

        self.rename_figure_btn = QPushButton("Rename")
        self.rename_figure_btn.setMaximumWidth(80)
        self.rename_figure_btn.clicked.connect(self._rename_figure)
        figure_layout.addWidget(self.rename_figure_btn)

        self.delete_figure_btn = QPushButton("Delete")
        self.delete_figure_btn.setMaximumWidth(80)
        self.delete_figure_btn.clicked.connect(self._delete_figure)
        figure_layout.addWidget(self.delete_figure_btn)

        self.import_figure_btn = QPushButton("Import...")
        self.import_figure_btn.setMaximumWidth(80)
        self.import_figure_btn.clicked.connect(self._import_figure)
        figure_layout.addWidget(self.import_figure_btn)

        self.export_figure_btn = QPushButton("Export...")
        self.export_figure_btn.setMaximumWidth(80)
        self.export_figure_btn.clicked.connect(self._export_figure)
        figure_layout.addWidget(self.export_figure_btn)

        center_layout.addWidget(figure_group)

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

        self.hover_info_checkbox = QCheckBox("Show Hover Info")
        self.hover_info_checkbox.setChecked(False)  # Start disabled
        self.hover_info_checkbox.toggled.connect(self._on_hover_info_toggled)
        display_layout.addWidget(self.hover_info_checkbox)

        # Border color
        border_color_layout = QHBoxLayout()
        border_color_layout.addWidget(QLabel("Border Color:"))
        self.border_color_combo = create_color_combo()
        self.border_color_combo.setCurrentIndex(0)  # Black
        self.border_color_combo.currentIndexChanged.connect(self._on_border_color_changed)
        border_color_layout.addWidget(self.border_color_combo)
        display_layout.addLayout(border_color_layout)

        right_layout.addWidget(display_group)

        # Display mode group
        mode_group = QGroupBox("Display Mode")
        mode_layout = QVBoxLayout(mode_group)

        # Radio buttons for mode selection
        self.mode_button_group = QButtonGroup(self)

        self.color_stack_radio = QRadioButton("Color Stack Mode")
        self.color_stack_radio.setChecked(True)  # Default mode
        self.color_stack_radio.toggled.connect(self._on_mode_changed)
        self.mode_button_group.addButton(self.color_stack_radio, 0)
        mode_layout.addWidget(self.color_stack_radio)

        self.fg_bg_radio = QRadioButton("Foreground/Background Mode")
        self.fg_bg_radio.toggled.connect(self._on_mode_changed)
        self.mode_button_group.addButton(self.fg_bg_radio, 1)
        mode_layout.addWidget(self.fg_bg_radio)

        right_layout.addWidget(mode_group)

        # Selected BACKTAB card group
        tile_group = QGroupBox("Selected BACKTAB Card")
        tile_layout = QVBoxLayout(tile_group)

        self.tile_info_label = QLabel("No card selected")
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
        fg_color_layout = QHBoxLayout()
        fg_color_layout.addWidget(QLabel("FG Color:"))
        self.fg_color_combo = create_color_combo()
        self.fg_color_combo.setCurrentIndex(7)  # White
        self.fg_color_combo.currentIndexChanged.connect(self._on_fg_color_changed)
        fg_color_layout.addWidget(self.fg_color_combo)
        tile_layout.addLayout(fg_color_layout)

        # Background color (FG/BG mode only)
        self.bg_color_layout = QHBoxLayout()
        self.bg_color_label = QLabel("BG Color:")
        self.bg_color_layout.addWidget(self.bg_color_label)
        self.bg_color_combo = create_color_combo()
        self.bg_color_combo.setCurrentIndex(0)  # Black
        self.bg_color_combo.currentIndexChanged.connect(self._on_bg_color_changed)
        self.bg_color_layout.addWidget(self.bg_color_combo)
        tile_layout.addLayout(self.bg_color_layout)

        # Advance stack checkbox (Color Stack mode only)
        self.advance_stack_checkbox = QCheckBox("Advance Color Stack")
        self.advance_stack_checkbox.toggled.connect(self._on_advance_stack_toggled)
        tile_layout.addWidget(self.advance_stack_checkbox)

        right_layout.addWidget(tile_group)

        # Color stack group (Color Stack mode only)
        self.stack_group = QGroupBox("Color Stack")
        stack_layout = QVBoxLayout(self.stack_group)

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

        right_layout.addWidget(self.stack_group)

        # MOBs (Moving Object Blocks)
        mobs_label = QLabel("<b>MOBs</b>")
        right_layout.addWidget(mobs_label)

        # Create scrollable area for MOBs
        mobs_scroll = QScrollArea()
        mobs_scroll.setWidgetResizable(True)
        mobs_scroll.setMaximumHeight(300)  # Limit height to make it scrollable

        mobs_group = QGroupBox()
        mobs_layout = QVBoxLayout(mobs_group)
        mobs_layout.setSpacing(4)

        # Store MOB controls for each of 8 MOBs
        self.mob_controls = []

        for mob_idx in range(8):
            controls = {}

            # Row 1: Visibility, MOB#, Card, X, Y
            mob_row1 = QHBoxLayout()
            mob_row1.setSpacing(4)

            # Visibility checkbox
            controls['visible'] = QCheckBox()
            controls['visible'].setMaximumWidth(20)
            mob_row1.addWidget(controls['visible'])

            # MOB number label
            mob_label = QLabel(f"{mob_idx}:")
            mob_label.setMaximumWidth(15)
            mob_row1.addWidget(mob_label)

            # GRAM# dropdown (cards 256-319, MOBs can only use GRAM)
            controls['card'] = QComboBox()
            controls['card'].setMaximumWidth(70)
            for card_num in range(256, 320):
                controls['card'].addItem(f"{card_num}")
            controls['card'].setCurrentIndex(0)  # Default to GRAM card 256
            mob_row1.addWidget(controls['card'])

            # X position (INTV world coordinates: 0-175)
            mob_row1.addWidget(QLabel("X"))
            controls['x'] = QSpinBox()
            controls['x'].setRange(0, 175)  # 8px border + 160px playfield + 8px border - 1
            controls['x'].setMaximumWidth(50)
            mob_row1.addWidget(controls['x'])

            # Y position (INTV world coordinates: 0-111)
            mob_row1.addWidget(QLabel("Y"))
            controls['y'] = QSpinBox()
            controls['y'].setRange(0, 111)  # 8px border + 96px playfield + 8px border - 1
            controls['y'].setMaximumWidth(50)
            mob_row1.addWidget(controls['y'])

            mob_row1.addStretch()
            mobs_layout.addLayout(mob_row1)

            # Row 2: Color, Priority, Size, H/V flip (indented)
            mob_row2 = QHBoxLayout()
            mob_row2.setSpacing(4)
            mob_row2.addSpacing(35)  # Indent to align with row 1 controls

            # Color (compact: just swatch + number)
            mob_row2.addWidget(QLabel("C:"))
            controls['color'] = QComboBox()
            controls['color'].setMaximumWidth(55)
            for i in range(16):
                pixmap = QPixmap(12, 12)
                pixmap.fill(QColor(get_color_hex(i)))
                controls['color'].addItem(pixmap, f"{i}")
            controls['color'].setCurrentIndex(7)  # White
            mob_row2.addWidget(controls['color'])

            # Priority checkbox (F/B = Front/Back)
            controls['priority'] = QCheckBox("F/B")
            controls['priority'].setMaximumWidth(40)
            mob_row2.addWidget(controls['priority'])

            # Size dropdown
            mob_row2.addWidget(QLabel("S:"))
            controls['size'] = QComboBox()
            controls['size'].setMaximumWidth(60)
            controls['size'].addItems(["8x8", "8x16", "16x8", "16x16"])
            mob_row2.addWidget(controls['size'])

            # Horizontal flip
            controls['h_flip'] = QCheckBox("H")
            controls['h_flip'].setMaximumWidth(30)
            mob_row2.addWidget(controls['h_flip'])

            # Vertical flip
            controls['v_flip'] = QCheckBox("V")
            controls['v_flip'].setMaximumWidth(30)
            mob_row2.addWidget(controls['v_flip'])

            mob_row2.addStretch()
            mobs_layout.addLayout(mob_row2)

            # Add separator line between MOBs (except after last one)
            if mob_idx < 7:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                mobs_layout.addWidget(separator)

            self.mob_controls.append(controls)

        mobs_scroll.setWidget(mobs_group)
        right_layout.addWidget(mobs_scroll)

        # Connect MOB control signals
        for mob_idx, controls in enumerate(self.mob_controls):
            controls['visible'].toggled.connect(lambda checked, idx=mob_idx: self._on_mob_visible_changed(idx, checked))
            controls['card'].currentIndexChanged.connect(lambda card, idx=mob_idx: self._on_mob_card_changed(idx, card))
            controls['x'].valueChanged.connect(lambda x, idx=mob_idx: self._on_mob_x_changed(idx, x))
            controls['y'].valueChanged.connect(lambda y, idx=mob_idx: self._on_mob_y_changed(idx, y))
            controls['color'].currentIndexChanged.connect(lambda color, idx=mob_idx: self._on_mob_color_changed(idx, color))
            controls['priority'].toggled.connect(lambda checked, idx=mob_idx: self._on_mob_priority_changed(idx, checked))
            controls['size'].currentIndexChanged.connect(lambda size, idx=mob_idx: self._on_mob_size_changed(idx, size))
            controls['h_flip'].toggled.connect(lambda checked, idx=mob_idx: self._on_mob_hflip_changed(idx, checked))
            controls['v_flip'].toggled.connect(lambda checked, idx=mob_idx: self._on_mob_vflip_changed(idx, checked))

        right_layout.addStretch()

        main_layout.addWidget(right_panel)

        # Initialize data
        self._update_palette()
        self._update_canvas_data()
        self._refresh_figure_list()

        # Current selection state
        self.current_card = 0
        self.current_fg_color = 7
        self.current_bg_color = 0  # Black (FG/BG mode only)
        self.selected_row = None
        self.selected_col = None

        # Set initial UI visibility based on default mode (Color Stack)
        self._update_mode_ui()

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
            # Explicitly load the first figure (in case signal doesn't fire)
            self.current_figure = self.project.stic_figures[0]
            self._load_figure(self.current_figure)

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
        if self.project:
            gram_data = []
            for i in range(64):
                card = self.project.get_card(i)
                if card is not None:
                    gram_data.append(card.to_bytes())
                else:
                    gram_data.append([0] * 8)  # Empty card
            if self.grom_data:
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
            # Calculate BACKTAB card number (0-239)
            backtab_card = row * 20 + col
            # Calculate world coordinates (accounting for 8px border)
            world_x = col * 8 + 8
            world_y = row * 8 + 8
            self.tile_info_label.setText(
                f"Card: {backtab_card}, Row: {row}, Col: {col}\n"
                f"World: X={world_x}, Y={world_y}"
            )

            self.card_spin.blockSignals(True)
            self.card_spin.setValue(tile['card'])
            self.card_spin.blockSignals(False)

            self.fg_color_combo.blockSignals(True)
            self.fg_color_combo.setCurrentIndex(tile['fg_color'])
            self.fg_color_combo.blockSignals(False)

            # Update BG color if tile has it
            if 'bg_color' in tile:
                self.bg_color_combo.blockSignals(True)
                self.bg_color_combo.setCurrentIndex(tile['bg_color'])
                self.bg_color_combo.blockSignals(False)

            self.advance_stack_checkbox.blockSignals(True)
            self.advance_stack_checkbox.setChecked(tile['advance_stack'])
            self.advance_stack_checkbox.blockSignals(False)

            # Update current card/color to match tile (eyedropper effect)
            self.current_card = tile['card']
            self.current_fg_color = tile['fg_color']
            if 'bg_color' in tile:
                self.current_bg_color = tile['bg_color']

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
                bg_color=self.current_bg_color,
                advance_stack=self.advance_stack_checkbox.isChecked()
            )
            # Update current figure if one is loaded
            if self.current_figure:
                self.current_figure.set_tile(
                    self.selected_row,
                    self.selected_col,
                    self.current_card,
                    self.current_fg_color,
                    bg_color=self.current_bg_color,
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

    def _on_bg_color_changed(self, index):
        """Handle background color change (FG/BG mode only)"""
        self.current_bg_color = index
        if self.selected_row is not None and self.selected_col is not None:
            self._apply_current_to_selected()

    def _on_mode_changed(self, checked):
        """Handle display mode change"""
        if not checked:  # Only process when radio is checked, not unchecked
            return

        # Update figure mode if there is one
        if self.current_figure:
            if self.color_stack_radio.isChecked():
                self.current_figure.mode = "color_stack"
            else:
                self.current_figure.mode = "fg_bg"

            # Update canvas display mode
            self.canvas.display_mode = self.current_figure.mode

        # Update UI visibility
        self._update_mode_ui()
        self.canvas.update()

    def _update_mode_ui(self):
        """Update UI control visibility based on current display mode"""
        # Check which radio button is selected (works even without current_figure)
        is_color_stack = self.color_stack_radio.isChecked()

        # Show/hide BG color controls (FG/BG mode only)
        self.bg_color_label.setVisible(not is_color_stack)
        self.bg_color_combo.setVisible(not is_color_stack)

        # Show/hide advance stack checkbox (Color Stack mode only)
        self.advance_stack_checkbox.setVisible(is_color_stack)

        # Show/hide Color Stack group (Color Stack mode only)
        self.stack_group.setVisible(is_color_stack)

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

    def _on_hover_info_toggled(self, checked):
        """Handle hover info visibility toggle"""
        self.canvas.show_hover_info = checked
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

        # Clear canvas first to ensure no old data persists
        self.canvas.clear_all_tiles()

        # Update canvas border settings
        self.canvas.border_visible = figure.border_visible
        self.canvas.border_color = figure.border_color
        self.canvas.show_left_border = figure.show_left_border
        self.canvas.show_top_border = figure.show_top_border

        # Update border UI
        self.border_checkbox.setChecked(figure.border_visible)
        self.border_color_combo.setCurrentIndex(figure.border_color)

        # Update display mode
        self.canvas.display_mode = figure.mode
        if figure.mode == "color_stack":
            self.color_stack_radio.setChecked(True)
        else:
            self.fg_bg_radio.setChecked(True)
        self._update_mode_ui()

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
                bg_color=tile_data.get("bg_color", 0),
                advance_stack=tile_data.get("advance_stack", False)
            )

        # Load MOB data into canvas
        self.canvas.mobs = [mob.copy() for mob in figure.mobs]

        # Load MOB data into UI controls
        self._load_mobs_from_figure(figure)

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

    # MOB control handlers
    def _on_mob_visible_changed(self, mob_idx, checked):
        """Handle MOB visibility checkbox change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['visible'] = checked
            self.canvas.mobs[mob_idx]['visible'] = checked
            self.canvas.update()

    def _on_mob_card_changed(self, mob_idx, card_idx):
        """Handle MOB card dropdown change"""
        if self.current_figure:
            # Dropdown shows cards 256-319, so add 256 to index
            card = 256 + card_idx
            self.current_figure.mobs[mob_idx]['card'] = card
            self.canvas.mobs[mob_idx]['card'] = card
            self.canvas.update()

    def _on_mob_x_changed(self, mob_idx, x):
        """Handle MOB X position change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['x'] = x
            self.canvas.mobs[mob_idx]['x'] = x
            self.canvas.update()

    def _on_mob_y_changed(self, mob_idx, y):
        """Handle MOB Y position change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['y'] = y
            self.canvas.mobs[mob_idx]['y'] = y
            self.canvas.update()

    def _on_mob_color_changed(self, mob_idx, color):
        """Handle MOB color dropdown change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['color'] = color
            self.canvas.mobs[mob_idx]['color'] = color
            self.canvas.update()

    def _on_mob_priority_changed(self, mob_idx, checked):
        """Handle MOB priority checkbox change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['priority'] = checked
            self.canvas.mobs[mob_idx]['priority'] = checked
            self.canvas.update()

    def _on_mob_size_changed(self, mob_idx, size_idx):
        """Handle MOB size dropdown change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['size'] = size_idx
            self.canvas.mobs[mob_idx]['size'] = size_idx
            self.canvas.update()

    def _on_mob_hflip_changed(self, mob_idx, checked):
        """Handle MOB horizontal flip checkbox change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['h_flip'] = checked
            self.canvas.mobs[mob_idx]['h_flip'] = checked
            self.canvas.update()

    def _on_mob_vflip_changed(self, mob_idx, checked):
        """Handle MOB vertical flip checkbox change"""
        if self.current_figure:
            self.current_figure.mobs[mob_idx]['v_flip'] = checked
            self.canvas.mobs[mob_idx]['v_flip'] = checked
            self.canvas.update()

    def _load_mobs_from_figure(self, figure):
        """Load MOB data from figure into UI controls"""
        if not figure:
            return

        for mob_idx in range(8):
            mob_data = figure.mobs[mob_idx]
            controls = self.mob_controls[mob_idx]

            # Block signals while updating to avoid triggering save
            controls['visible'].blockSignals(True)
            controls['card'].blockSignals(True)
            controls['x'].blockSignals(True)
            controls['y'].blockSignals(True)
            controls['color'].blockSignals(True)
            controls['priority'].blockSignals(True)
            controls['size'].blockSignals(True)
            controls['h_flip'].blockSignals(True)
            controls['v_flip'].blockSignals(True)

            # Set values
            controls['visible'].setChecked(mob_data['visible'])
            # Card dropdown shows 256-319, so subtract 256 to get index
            controls['card'].setCurrentIndex(mob_data['card'] - 256)
            controls['x'].setValue(mob_data['x'])
            controls['y'].setValue(mob_data['y'])
            controls['color'].setCurrentIndex(mob_data['color'])
            controls['priority'].setChecked(mob_data['priority'])
            controls['size'].setCurrentIndex(mob_data['size'])
            controls['h_flip'].setChecked(mob_data['h_flip'])
            controls['v_flip'].setChecked(mob_data['v_flip'])

            # Unblock signals
            controls['visible'].blockSignals(False)
            controls['card'].blockSignals(False)
            controls['x'].blockSignals(False)
            controls['y'].blockSignals(False)
            controls['color'].blockSignals(False)
            controls['priority'].blockSignals(False)
            controls['size'].blockSignals(False)
            controls['h_flip'].blockSignals(False)
            controls['v_flip'].blockSignals(False)
