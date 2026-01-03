"""
GROM (Graphics ROM) character browser widget.

Displays all 256 built-in Intellivision GROM characters in a read-only grid.
Helps users reference available characters and avoid wasting GRAM slots.
"""

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QVBoxLayout, QScrollArea, QFrame,
    QMenu, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QAction

from telligram.core.grom import GromData


class GromThumbnail(QFrame):
    """
    Thumbnail widget displaying a single GROM character.
    Uses QPixmap for WSL compatibility instead of custom paintEvent.

    Shows the 8x8 character graphic with its card number and label.
    """

    clicked = Signal(int)  # Emits card number when clicked
    copy_to_gram_requested = Signal(int)  # Emits GROM card number to copy

    def __init__(self, card_num: int, grom: GromData, parent=None):
        super().__init__(parent)
        self.card_num = card_num
        self.grom = grom
        self.card_data = self.grom.get_card(card_num)
        self.label_text = self.grom.get_label(card_num)

        # Smaller thumbnails than GRAM grid (we have 256 cards!)
        self.pixel_size = 6
        self.setFixedSize(60, 80)  # Width: 60px, Height: 80px (extra space for labels)

        # Create UI elements
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # Card number label
        self.num_label = QLabel(f"#{card_num}")
        self.num_label.setStyleSheet("color: #787878; font-size: 9px;")
        layout.addWidget(self.num_label)

        # Character preview (QLabel displaying QPixmap)
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(48, 48)
        self.preview_label.setAlignment(Qt.AlignCenter)
        pixmap = self._render_character()
        self.preview_label.setPixmap(pixmap)
        layout.addWidget(self.preview_label)

        # Character label
        self.char_label = QLabel(self.label_text[:10])  # Truncate long labels
        self.char_label.setStyleSheet("color: #969696; font-size: 8px;")
        self.char_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.char_label)

        # Style
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
            }
            QFrame:hover {
                background-color: #3c3c3c;
                border: 1px solid #5c5c5c;
            }
            QLabel {
                background-color: transparent;
            }
        """)

    def _render_character(self) -> QPixmap:
        """Render GROM character to QPixmap - more WSL-compatible than direct painting"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)

        # Draw the 8x8 graphic
        for y in range(8):
            row_byte = self.card_data[y]
            for x in range(8):
                bit = 7 - x
                pixel_on = (row_byte >> bit) & 1

                # Draw pixel
                if pixel_on:
                    painter.fillRect(
                        x * self.pixel_size,
                        y * self.pixel_size,
                        self.pixel_size,
                        self.pixel_size,
                        QColor(200, 200, 200)
                    )

        painter.end()
        return pixmap

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.card_num)

    def contextMenuEvent(self, event):
        """Handle right-click context menu"""
        menu = QMenu(self)
        copy_action = QAction(f"Copy GROM #{self.card_num} to GRAM...", self)
        copy_action.triggered.connect(lambda: self.copy_to_gram_requested.emit(self.card_num))
        menu.addAction(copy_action)
        menu.exec(event.globalPos())


class GromBrowserWidget(QWidget):
    """
    GROM character browser widget.

    Displays all 256 GROM characters in a scrollable grid.
    Read-only reference for users to see available built-in characters.
    """

    card_selected = Signal(int)  # Emits when a card is clicked
    copy_to_gram_requested = Signal(int)  # Emits GROM card number to copy to GRAM

    def __init__(self, grom_path=None, parent=None):
        super().__init__(parent)
        self.grom = GromData(grom_path)
        self.thumbnails = []
        self._create_ui()

    def _create_ui(self):
        """Create the UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        title = QLabel("GROM Characters (0-255)")
        title.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: #1e1e1e;
            }
        """)
        main_layout.addWidget(title)

        # Scroll area for the grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
        """)

        # Container for the grid
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setSpacing(2)
        grid_layout.setContentsMargins(4, 4, 4, 4)

        # Create 256 thumbnails in 16x16 grid
        for i in range(256):
            thumb = GromThumbnail(i, self.grom)
            thumb.clicked.connect(self._on_thumbnail_clicked)
            thumb.copy_to_gram_requested.connect(self._on_copy_to_gram_requested)
            self.thumbnails.append(thumb)

            row = i // 16
            col = i % 16
            grid_layout.addWidget(thumb, row, col)

        # Set minimum width to fit all 16 columns
        # 16 cols * 60px + 15 gaps * 2px + margins 8px = 998px
        container.setMinimumWidth(998)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _on_thumbnail_clicked(self, card_num: int):
        """Handle thumbnail click"""
        self.card_selected.emit(card_num)

    def _on_copy_to_gram_requested(self, grom_card_num: int):
        """Handle copy to GRAM request"""
        self.copy_to_gram_requested.emit(grom_card_num)

    def get_card_data(self, card_num: int):
        """Get GROM card data by number"""
        return self.grom.get_card(card_num)

    def get_card_label(self, card_num: int):
        """Get label for GROM card"""
        return self.grom.get_label(card_num)
