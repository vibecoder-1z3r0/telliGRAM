"""Card grid widget - displays all 64 GRAM card slots"""
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen

from telligram.core.project import Project
from telligram.core.card import GramCard


class CardThumbnail(QWidget):
    """Thumbnail view of a single card"""

    clicked = Signal(int)  # Emits slot number when clicked

    def __init__(self, slot: int):
        super().__init__()
        self.slot = slot
        self.card = None
        self.selected = False
        self.setFixedSize(70, 90)

    def set_card(self, card: GramCard):
        """Set card to display"""
        self.card = card
        self.update()  # Trigger repaint

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.selected = selected
        self.update()  # Trigger repaint

    def mousePressEvent(self, event):
        """Handle mouse click"""
        self.clicked.emit(self.slot)

    def paintEvent(self, event):
        """Paint the card thumbnail"""
        painter = QPainter(self)

        # Background
        if self.selected:
            painter.fillRect(0, 0, self.width(), self.height(), QColor("#0078D4"))
            painter.setPen(QPen(QColor("#0078D4"), 2))
        else:
            painter.fillRect(0, 0, self.width(), self.height(), QColor("#2b2b2b"))
            painter.setPen(QPen(QColor("#3c3c3c"), 1))

        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Draw slot number
        painter.setPen(QColor(180, 180, 180) if self.selected else QColor(120, 120, 120))
        painter.drawText(5, 12, f"#{self.slot}")

        # Draw preview area background
        preview_x = 5
        preview_y = 20
        preview_size = 60

        painter.fillRect(preview_x, preview_y, preview_size, preview_size, QColor("#1a1a1a"))
        painter.setPen(QColor("#444"))
        painter.drawRect(preview_x, preview_y, preview_size, preview_size)

        if self.card is None:
            return

        # Draw card pixels (8×8 scaled to 56×56, centered in 60×60)
        pixel_size = 7
        offset_x = preview_x + 2  # Center the 56px grid in 60px area
        offset_y = preview_y + 2

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
