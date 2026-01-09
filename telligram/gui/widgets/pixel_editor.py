"""Pixel editor widget - 8×8 grid for editing GRAM cards"""

from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QMouseEvent

from telligram.core.card import GramCard
from telligram.core.constants import get_color_hex


class PixelEditorWidget(QWidget):
    """8×8 pixel editor for GRAM cards"""

    card_changed = Signal()  # Emitted when card is modified

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.card = None
        self.pixel_size = 40  # Pixels are 40×40 on screen
        self.grid_size = 8
        self.drawing = False
        self.draw_value = 1  # 1 = set pixel, 0 = erase
        self.stroke_start_data = None  # Card state at start of stroke
        self.show_grid = True  # Grid visible by default

        # Calculate total size
        total_size = self.pixel_size * self.grid_size
        self.setFixedSize(total_size, total_size)
        self.setMouseTracking(True)

        # Create empty card if none provided
        if self.card is None:
            self.card = GramCard()

    def set_card(self, card: GramCard):
        """Set card to edit"""
        if card is None:
            self.card = GramCard()
        else:
            self.card = card
        self.update()

    def get_card(self) -> GramCard:
        """Get current card"""
        return self.card

    def clear_card(self):
        """Clear all pixels"""
        if self.card:
            self.card.clear()
            self.update()
            self.card_changed.emit()

    def set_grid_visible(self, visible: bool):
        """Toggle grid visibility"""
        self.show_grid = visible
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            # Store card state at start of stroke for undo
            if self.card:
                self.stroke_start_data = self.card.to_bytes()

            self.drawing = True
            x, y = self._get_pixel_coords(event.pos().x(), event.pos().y())
            if x is not None:
                # Determine if we're setting or erasing based on current pixel
                current = self.card.get_pixel(x, y)
                self.draw_value = 1 if current == 0 else 0
                self._set_pixel(x, y)
        elif event.button() == Qt.RightButton:
            # Store card state at start of stroke for undo
            if self.card:
                self.stroke_start_data = self.card.to_bytes()

            # Right click = erase
            self.drawing = True
            self.draw_value = 0
            x, y = self._get_pixel_coords(event.pos().x(), event.pos().y())
            if x is not None:
                self._set_pixel(x, y)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse drag"""
        if self.drawing:
            x, y = self._get_pixel_coords(event.pos().x(), event.pos().y())
            if x is not None:
                self._set_pixel(x, y)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        self.drawing = False

        # Create undo command for this stroke if something changed
        if self.main_window and self.stroke_start_data and self.card:
            current_data = self.card.to_bytes()
            # Only create command if card actually changed
            if current_data != self.stroke_start_data:
                from telligram.gui.main_window import PixelEditCommand

                command = PixelEditCommand(
                    self.main_window,
                    self.main_window.current_card_slot,
                    self.stroke_start_data,
                    current_data,
                )
                self.main_window.undo_stack.push(command)

        self.stroke_start_data = None

    def _get_pixel_coords(self, mouse_x: int, mouse_y: int):
        """Convert mouse coordinates to pixel coordinates"""
        x = mouse_x // self.pixel_size
        y = mouse_y // self.pixel_size

        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return x, y
        return None, None

    def _set_pixel(self, x: int, y: int):
        """Set pixel and update display"""
        if self.card:
            self.card.set_pixel(x, y, self.draw_value)
            self.update()
            self.card_changed.emit()

    def paintEvent(self, event):
        """Paint the grid and pixels"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Draw background
        painter.fillRect(0, 0, self.width(), self.height(), QColor("#1E1E1E"))

        if self.card is None:
            return

        # Get card color
        card_color = (
            get_color_hex(self.card.color) if hasattr(self.card, "color") else "#FFFFFF"
        )

        # Draw pixels
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                px = x * self.pixel_size
                py = y * self.pixel_size

                # Draw pixel
                if self.card.get_pixel(x, y):
                    painter.fillRect(
                        px, py, self.pixel_size, self.pixel_size, QColor(card_color)
                    )
                else:
                    painter.fillRect(
                        px, py, self.pixel_size, self.pixel_size, QColor("#2D2D30")
                    )

        # Draw grid lines (if enabled)
        if self.show_grid:
            painter.setPen(QPen(QColor("#3E3E42"), 1))

            # Vertical lines
            for x in range(self.grid_size + 1):
                px = x * self.pixel_size
                painter.drawLine(px, 0, px, self.height())

            # Horizontal lines
            for y in range(self.grid_size + 1):
                py = y * self.pixel_size
                painter.drawLine(0, py, self.width(), py)

        # Draw thicker border
        painter.setPen(QPen(QColor("#666666"), 2))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
