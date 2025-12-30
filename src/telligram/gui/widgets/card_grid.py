"""Card grid widget - displays all 64 GRAM card slots"""
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen

from telligram.core.project import Project
from telligram.core.card import GramCard


class CardThumbnail(QFrame):
    """Thumbnail view of a single card"""

    clicked = Signal(int)  # Emits slot number when clicked

    def __init__(self, slot: int):
        super().__init__()
        self.slot = slot
        self.card = None
        self.selected = False

        self.setFixedSize(70, 90)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setLineWidth(2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.label = QLabel(f"#{slot}")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.preview = QLabel()
        self.preview.setFixedSize(60, 60)
        self.preview.setStyleSheet("background-color: #222; border: 1px solid #444;")
        layout.addWidget(self.preview)

    def set_card(self, card: GramCard):
        """Set card to display"""
        self.card = card
        self.update()

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.selected = selected
        if selected:
            self.setStyleSheet("CardThumbnail { border: 2px solid #0078D4; background: #E6F2FF; }")
        else:
            self.setStyleSheet("")
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse click"""
        self.clicked.emit(self.slot)

    def paintEvent(self, event):
        """Custom paint for card preview"""
        super().paintEvent(event)

        if self.card is None:
            return

        # Draw card preview (zoomed 7.5x to fit 60×60 area)
        painter = QPainter(self.preview)
        pixel_size = 7  # 60÷8 = 7.5, use 7 for clean pixels

        for y in range(8):
            for x in range(8):
                if self.card.get_pixel(x, y):
                    painter.fillRect(
                        x * pixel_size + 2,
                        y * pixel_size + 2,
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
