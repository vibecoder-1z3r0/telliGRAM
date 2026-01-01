"""Color palette widget for selecting Intellivision colors"""
from PySide6.QtWidgets import QWidget, QGridLayout, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen

from telligram.core.constants import INTELLIVISION_PALETTE


class ColorSwatch(QFrame):
    """Individual color swatch button"""

    clicked = Signal(int)  # Emits color index when clicked

    def __init__(self, color_index: int):
        super().__init__()
        self.color_index = color_index
        self.color_data = INTELLIVISION_PALETTE[color_index]
        self.is_selected = False

        self.setFixedSize(28, 28)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setCursor(Qt.PointingHandCursor)

        # Tooltip showing color name
        self.setToolTip(f"{self.color_data['name']} (#{color_index})")

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        self.update()

    def mousePressEvent(self, event):
        """Handle click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.color_index)

    def paintEvent(self, event):
        """Paint color swatch"""
        super().paintEvent(event)

        painter = QPainter(self)

        # Fill with color
        color = QColor(self.color_data["hex"])
        painter.fillRect(2, 2, 24, 24, color)

        # Draw selection indicator
        if self.is_selected:
            # Thick white border inside the frame
            painter.setPen(QPen(QColor("#FFFFFF"), 3))
            painter.drawRect(4, 4, 19, 19)
            # Black outline for contrast
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.drawRect(3, 3, 21, 21)


class ColorPaletteWidget(QWidget):
    """Color palette widget showing 16 Intellivision colors in 2×8 grid"""

    color_selected = Signal(int)  # Emits color index (0-15) when selected

    def __init__(self):
        super().__init__()
        self.current_color = 7  # Default to White
        self.swatches = []
        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Create 2 rows × 8 columns grid
        # Row 0: Primary palette (0-7)
        # Row 1: Extended palette (8-15)
        for i in range(16):
            row = i // 8
            col = i % 8

            swatch = ColorSwatch(i)
            swatch.clicked.connect(self._on_swatch_clicked)
            layout.addWidget(swatch, row, col)
            self.swatches.append(swatch)

        # Highlight default color
        self.swatches[self.current_color].set_selected(True)

    def set_color(self, color_index: int):
        """Set currently selected color"""
        if 0 <= color_index < 16:
            # Deselect old
            self.swatches[self.current_color].set_selected(False)
            # Select new
            self.current_color = color_index
            self.swatches[self.current_color].set_selected(True)

    def get_color(self) -> int:
        """Get currently selected color index"""
        return self.current_color

    def _on_swatch_clicked(self, color_index: int):
        """Handle swatch click"""
        if color_index != self.current_color:
            self.set_color(color_index)
            self.color_selected.emit(color_index)
