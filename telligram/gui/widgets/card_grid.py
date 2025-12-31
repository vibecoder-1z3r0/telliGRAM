"""Card grid widget - displays all 64 GRAM card slots"""
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap

from telligram.core.project import Project
from telligram.core.card import GramCard


class CardThumbnail(QFrame):
    """Thumbnail view of a single card with visual preview"""

    clicked = Signal(int)  # Emits slot number when clicked

    def __init__(self, slot: int):
        super().__init__()
        self.slot = slot
        self.card = None
        self.selected = False
        self.setFixedSize(70, 90)

        # Create UI elements
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(0)

        # Slot number label
        self.slot_label = QLabel(f"#{slot}")
        self.slot_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.slot_label)

        # Card preview (QLabel displaying QPixmap) - centered
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(60, 60)
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # Set initial style
        self._update_style()

    def _render_card(self) -> QPixmap:
        """Render card to QPixmap"""
        pixmap = QPixmap(60, 60)
        pixmap.fill(QColor("#1a1a1a"))

        if self.card is None:
            return pixmap

        painter = QPainter(pixmap)
        painter.setPen(QColor("#444"))
        painter.drawRect(0, 0, 59, 59)

        # Draw card pixels (8×8 scaled to 56×56, centered in 60×60)
        pixel_size = 7
        offset_x = 2
        offset_y = 2

        for y in range(8):
            for x in range(8):
                if self.card.get_pixel(x, y):
                    painter.fillRect(
                        offset_x + x * pixel_size,
                        offset_y + y * pixel_size,
                        pixel_size,
                        pixel_size,
                        QColor("#FFFFFF")
                    )

        painter.end()
        return pixmap

    def _update_style(self):
        """Update visual style based on selection state"""
        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #0078D4;
                    border: 2px solid #0078D4;
                }
                QLabel {
                    color: #b4b4b4;
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #3c3c3c;
                }
                QLabel {
                    color: #787878;
                    background-color: transparent;
                }
            """)

    def set_card(self, card: GramCard):
        """Set card to display"""
        self.card = card
        pixmap = self._render_card()
        self.preview_label.setPixmap(pixmap)

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.selected = selected
        self._update_style()

    def mousePressEvent(self, event):
        """Handle mouse click"""
        self.clicked.emit(self.slot)


class CardGridWidget(QWidget):
    """Grid widget showing all 64 GRAM cards"""

    card_selected = Signal(int)  # Emits slot number when card selected

    def __init__(self):
        super().__init__()
        self.project = None
        self.thumbnails = []
        self.current_slot = 0

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        layout = QGridLayout(self)
        layout.setSpacing(4)

        # Create 64 thumbnails in 8×8 grid
        for i in range(64):
            thumb = CardThumbnail(i)
            thumb.clicked.connect(self.on_thumbnail_clicked)
            self.thumbnails.append(thumb)

            row = i // 8
            col = i % 8
            layout.addWidget(thumb, row, col)

    def set_project(self, project: Project):
        """Set project to display"""
        self.project = project

        # Update all thumbnails
        for i, thumb in enumerate(self.thumbnails):
            card = project.get_card(i)
            thumb.set_card(card)

        # Select first card
        self.select_card(0)

    def update_card(self, slot: int, card: GramCard):
        """Update specific card"""
        if 0 <= slot < 64:
            self.thumbnails[slot].set_card(card)

    def select_card(self, slot: int):
        """Select card by slot number"""
        # Deselect all
        for thumb in self.thumbnails:
            thumb.set_selected(False)

        # Select target
        if 0 <= slot < 64:
            self.thumbnails[slot].set_selected(True)
            self.current_slot = slot

    def on_thumbnail_clicked(self, slot: int):
        """Handle thumbnail click"""
        self.select_card(slot)
        self.card_selected.emit(slot)
