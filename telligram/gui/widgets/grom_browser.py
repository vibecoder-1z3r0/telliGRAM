"""
GROM (Graphics ROM) character browser widget.

Displays all 256 built-in Intellivision GROM characters in a read-only grid.
Helps users reference available characters and avoid wasting GRAM slots.
"""

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QMenu, QInputDialog, QCheckBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QAction

from telligram.core.grom import GromData
from telligram.core.constants import get_color_hex
from telligram.gui.widgets.color_palette import ColorPaletteWidget


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
        self.selected = False  # Selection state (match GRAM)

        # Match GRAM thumbnail size but add 10px for bottom label
        self.pixel_size = 7
        self.setFixedSize(70, 100)  # GRAM is 70x90, add 10px for character label

        # Create UI elements - match GRAM formatting
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add flexible space at top
        layout.addStretch()

        # Card number label (decimal and hex) - match GRAM format
        self.num_label = QLabel(f"#{card_num} ${card_num:02X}")
        self.num_label.setFixedWidth(60)
        self.num_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.num_label, alignment=Qt.AlignCenter)

        # Character preview (QLabel displaying QPixmap) - match GRAM size
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(60, 60)
        self.preview_label.setAlignment(Qt.AlignCenter)
        pixmap = self._render_character()
        self.preview_label.setPixmap(pixmap)
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # Character label - extra label not in GRAM (2px smaller font)
        self.char_label = QLabel(self.label_text[:10])  # Truncate long labels
        self.char_label.setStyleSheet("font-size: 11px;")
        self.char_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.char_label, alignment=Qt.AlignCenter)

        # Add flexible space at bottom
        layout.addStretch()

        # Set initial style
        self._update_style()

    def set_selected(self, selected: bool):
        """Set selection state (match GRAM)"""
        self.selected = selected
        self._update_style()

    def _update_style(self):
        """Update visual style based on selection state (match GRAM)"""
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

    def _render_character(self) -> QPixmap:
        """Render GROM character to QPixmap - more WSL-compatible than direct painting"""
        pixmap = QPixmap(60, 60)
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
                        QColor(255, 255, 255)  # White to match GRAM thumbnails
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


class GromPreviewWidget(QWidget):
    """
    Large preview widget for viewing selected GROM character.

    Read-only display with color selection to preview character in different colors.
    Similar to GRAM pixel editor but without editing capability.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.card_data = None
        self.card_num = 0
        self.preview_color = 7  # Default to white
        self.pixel_size = 40  # Match GRAM editor size
        self.grid_size = 8
        self.show_grid = True  # Grid visible by default
        self.flip_h = False  # Horizontal flip transform
        self.flip_v = False  # Vertical flip transform

        # Calculate total size (same as GRAM pixel editor)
        total_size = self.pixel_size * self.grid_size
        self.setFixedSize(total_size, total_size)

    def set_card(self, card_num: int, card_data: list):
        """Set GROM card to preview"""
        self.card_num = card_num
        self.card_data = card_data
        self.update()

    def set_color(self, color_index: int):
        """Set preview color"""
        self.preview_color = color_index
        self.update()

    def set_grid_visible(self, visible: bool):
        """Toggle grid visibility"""
        self.show_grid = visible
        self.update()

    def toggle_flip_horizontal(self):
        """Toggle horizontal flip"""
        self.flip_h = not self.flip_h
        self.update()

    def toggle_flip_vertical(self):
        """Toggle vertical flip"""
        self.flip_v = not self.flip_v
        self.update()

    def clear_transforms(self):
        """Clear all transformations (flip H/V)"""
        self.flip_h = False
        self.flip_v = False
        self.update()

    def paintEvent(self, event):
        """Paint the grid and pixels"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Draw background
        painter.fillRect(0, 0, self.width(), self.height(), QColor("#1E1E1E"))

        if self.card_data is None:
            return

        # Get preview color
        card_color = get_color_hex(self.preview_color)

        # Draw pixels (with optional flip transformations)
        for y in range(self.grid_size):
            row_byte = self.card_data[y]
            for x in range(self.grid_size):
                # Apply flip transformations to display coordinates
                display_x = (7 - x) if self.flip_h else x
                display_y = (7 - y) if self.flip_v else y

                px = display_x * self.pixel_size
                py = display_y * self.pixel_size

                # Check if pixel is on (bit 7-x in row_byte)
                bit = 7 - x
                pixel_on = (row_byte >> bit) & 1

                # Draw pixel
                if pixel_on:
                    painter.fillRect(px, py, self.pixel_size, self.pixel_size, QColor(card_color))
                else:
                    painter.fillRect(px, py, self.pixel_size, self.pixel_size, QColor("#2D2D30"))

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
        painter.drawRect(0, 0, self.width()-1, self.height()-1)


class GromBrowserWidget(QWidget):
    """
    GROM character browser widget.

    Displays all 256 GROM characters in a scrollable grid with preview panel.
    Read-only reference for users to see available built-in characters.
    """

    card_selected = Signal(int)  # Emits when a card is clicked
    copy_to_gram_requested = Signal(int)  # Emits GROM card number to copy to GRAM

    def __init__(self, grom_path=None, parent=None):
        super().__init__(parent)
        self.grom = GromData(grom_path)
        self.thumbnails = []
        self.selected_card = 0
        self._create_ui()

        # Initialize preview with first card and select it
        self._update_preview(0)
        if len(self.thumbnails) > 0:
            self.thumbnails[0].set_selected(True)

    def _create_ui(self):
        """Create the UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        title = QLabel("GROM Cards (0-255)")
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

        # Split layout: grid on left, preview panel on right
        split_layout = QHBoxLayout()
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(0)

        # Left side: Scroll area for the grid
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
        # 16 cols * 70px + 15 gaps * 2px + margins 8px = 1158px
        container.setMinimumWidth(1158)

        scroll.setWidget(container)
        split_layout.addWidget(scroll)

        # Right side: Preview panel
        preview_panel = QWidget()
        # No explicit background - use default to match GRAM editor
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        preview_layout.setSpacing(12)

        # Card info label (match GRAM editor style)
        self.card_info_label = QLabel("<h3>GROM Card #0 $00</h3>")
        preview_layout.addWidget(self.card_info_label)

        # Preview widget
        self.preview_widget = GromPreviewWidget()
        preview_layout.addWidget(self.preview_widget, alignment=Qt.AlignTop)

        # Grid toggle checkbox
        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self._on_grid_toggled)
        preview_layout.addWidget(self.grid_checkbox)

        # Transform buttons (Clear, Flip H, Flip V)
        button_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._on_clear_transforms)
        button_layout.addWidget(clear_btn)

        flip_h_btn = QPushButton("Flip H")
        flip_h_btn.clicked.connect(self._on_flip_horizontal)
        button_layout.addWidget(flip_h_btn)

        flip_v_btn = QPushButton("Flip V")
        flip_v_btn.clicked.connect(self._on_flip_vertical)
        button_layout.addWidget(flip_v_btn)

        preview_layout.addLayout(button_layout)

        # Color palette
        palette_label = QLabel("Preview Color:")
        palette_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        preview_layout.addWidget(palette_label)

        self.color_palette = ColorPaletteWidget()
        self.color_palette.color_selected.connect(self._on_color_selected)
        preview_layout.addWidget(self.color_palette)

        preview_layout.addStretch()

        split_layout.addWidget(preview_panel)

        main_layout.addLayout(split_layout)

    def _on_thumbnail_clicked(self, card_num: int):
        """Handle thumbnail click"""
        # Deselect all thumbnails (match GRAM behavior)
        for thumb in self.thumbnails:
            thumb.set_selected(False)

        # Select clicked thumbnail
        if 0 <= card_num < len(self.thumbnails):
            self.thumbnails[card_num].set_selected(True)

        self.selected_card = card_num
        self._update_preview(card_num)
        self.card_selected.emit(card_num)

    def _on_copy_to_gram_requested(self, grom_card_num: int):
        """Handle copy to GRAM request"""
        self.copy_to_gram_requested.emit(grom_card_num)

    def _on_color_selected(self, color_index: int):
        """Handle color selection"""
        self.preview_widget.set_color(color_index)

    def _on_grid_toggled(self, state: int):
        """Handle grid toggle checkbox"""
        self.preview_widget.set_grid_visible(state == Qt.Checked)

    def _on_flip_horizontal(self):
        """Handle flip horizontal button"""
        self.preview_widget.toggle_flip_horizontal()

    def _on_flip_vertical(self):
        """Handle flip vertical button"""
        self.preview_widget.toggle_flip_vertical()

    def _on_clear_transforms(self):
        """Handle clear button - full reset to card #0 with default color"""
        # Reset transforms (flips)
        self.preview_widget.clear_transforms()

        # Reset color to default (white, color index 7)
        self.preview_widget.set_color(7)
        self.color_palette.set_color(7)

        # Reset card selection to card #0
        self._on_thumbnail_clicked(0)

    def _update_preview(self, card_num: int):
        """Update preview panel with selected card"""
        card_data = self.grom.get_card(card_num)
        card_label = self.grom.get_label(card_num)

        # Update card info label (match GRAM editor format)
        info_text = f"GROM Card #{card_num} ${card_num:02X}"
        if card_label:
            info_text += f" - {card_label}"
        self.card_info_label.setText(f"<h3>{info_text}</h3>")

        # Clear transforms when switching cards
        self.preview_widget.clear_transforms()

        # Update preview
        self.preview_widget.set_card(card_num, card_data)

    def get_card_data(self, card_num: int):
        """Get GROM card data by number"""
        return self.grom.get_card(card_num)

    def get_card_label(self, card_num: int):
        """Get label for GROM card"""
        return self.grom.get_label(card_num)
