"""
GROM (Graphics ROM) character browser widget.

Displays all 256 built-in Intellivision GROM characters in a read-only grid.
Helps users reference available characters and avoid wasting GRAM slots.
"""

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont

from telligram.core.grom import GromData


class GromThumbnail(QWidget):
    """
    Thumbnail widget displaying a single GROM character.

    Shows the 8x8 character graphic with its card number and label.
    """

    clicked = Signal(int)  # Emits card number when clicked

    def __init__(self, card_num: int, parent=None):
        super().__init__(parent)
        self.card_num = card_num
        self.grom = GromData()
        self.card_data = self.grom.get_card(card_num)
        self.label_text = self.grom.get_label(card_num)

        # Smaller thumbnails than GRAM grid (we have 256 cards!)
        self.pixel_size = 6
        self.setFixedSize(60, 80)  # Width: 60px, Height: 80px (extra space for labels)

        # Style
        self.setStyleSheet("""
            GromThumbnail {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
            }
            GromThumbnail:hover {
                background-color: #3c3c3c;
                border: 1px solid #5c5c5c;
            }
        """)

    def paintEvent(self, event):
        """Draw the GROM character"""
        super().paintEvent(event)
        painter = QPainter(self)

        # Draw card number
        painter.setPen(QColor(120, 120, 120))
        font = QFont()
        font.setPixelSize(9)
        painter.setFont(font)
        painter.drawText(2, 10, f"{self.card_num}")

        # Draw the 8x8 graphic
        start_y = 14
        for y in range(8):
            row_byte = self.card_data[y]
            for x in range(8):
                bit = 7 - x
                pixel_on = (row_byte >> bit) & 1

                # Draw pixel
                if pixel_on:
                    painter.fillRect(
                        6 + x * self.pixel_size,
                        start_y + y * self.pixel_size,
                        self.pixel_size,
                        self.pixel_size,
                        QColor(200, 200, 200)
                    )

        # Draw label (ASCII character or "Extended")
        painter.setPen(QColor(150, 150, 150))
        font.setPixelSize(8)
        painter.setFont(font)
        label_y = start_y + 8 * self.pixel_size + 10
        painter.drawText(4, label_y, self.label_text[:10])  # Truncate long labels

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.card_num)


class GromBrowserWidget(QWidget):
    """
    GROM character browser widget.

    Displays all 256 GROM characters in a scrollable grid.
    Read-only reference for users to see available built-in characters.
    """

    card_selected = Signal(int)  # Emits when a card is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grom = GromData()
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
            thumb = GromThumbnail(i)
            thumb.clicked.connect(self._on_thumbnail_clicked)
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

    def get_card_data(self, card_num: int):
        """Get GROM card data by number"""
        return self.grom.get_card(card_num)

    def get_card_label(self, card_num: int):
        """Get label for GROM card"""
        return self.grom.get_label(card_num)
