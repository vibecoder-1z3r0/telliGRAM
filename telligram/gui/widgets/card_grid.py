"""Card grid widget - displays all 64 GRAM card slots"""
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout,
    QMenu, QDialog, QTextEdit, QPushButton, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QAction, QFont

from telligram.core.project import Project
from telligram.core.card import GramCard
from telligram.core.constants import get_color_hex, INTELLIVISION_PALETTE


class CardThumbnail(QFrame):
    """Thumbnail view of a single card with visual preview"""

    clicked = Signal(int)  # Emits slot number when clicked

    def __init__(self, slot: int, parent_grid=None):
        super().__init__()
        self.slot = slot
        self.card = None
        self.selected = False
        self.parent_grid = parent_grid  # Reference to CardGridWidget for clipboard access
        self.setFixedSize(70, 90)

        # Create UI elements
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add flexible space at top
        layout.addStretch()

        # Slot number label - same width as preview for tab-like appearance
        self.slot_label = QLabel(f"#{slot}")
        self.slot_label.setFixedWidth(60)
        self.slot_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.slot_label, alignment=Qt.AlignCenter)

        # Card preview (QLabel displaying QPixmap) - centered
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(60, 60)
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # Add flexible space at bottom
        layout.addStretch()

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

        # Get card color
        card_color = get_color_hex(self.card.color) if hasattr(self.card, 'color') else "#FFFFFF"

        for y in range(8):
            for x in range(8):
                if self.card.get_pixel(x, y):
                    painter.fillRect(
                        offset_x + x * pixel_size,
                        offset_y + y * pixel_size,
                        pixel_size,
                        pixel_size,
                        QColor(card_color)
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
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.slot)

    def contextMenuEvent(self, event):
        """Handle right-click context menu"""
        has_card = self.card is not None and not self.card.is_empty()
        has_clipboard = self.parent_grid and self.parent_grid.has_clipboard_data()

        # Show menu if we have a card OR clipboard data
        if not has_card and not has_clipboard:
            return

        menu = QMenu(self)

        # Copy action (only if card exists)
        if has_card:
            copy_action = QAction("Copy Card", self)
            copy_action.triggered.connect(self._copy_card)
            menu.addAction(copy_action)

        # Paste action (only if clipboard has data)
        if has_clipboard:
            paste_action = QAction("Paste Card", self)
            paste_action.triggered.connect(self._paste_card)
            menu.addAction(paste_action)

        # Card operations (only if card exists)
        if has_card:
            if has_clipboard:
                menu.addSeparator()

            clear_action = QAction("Clear Card", self)
            clear_action.triggered.connect(self._clear_card)
            menu.addAction(clear_action)

            menu.addSeparator()

            flip_h_action = QAction("Flip Horizontal", self)
            flip_h_action.triggered.connect(self._flip_horizontal)
            menu.addAction(flip_h_action)

            flip_v_action = QAction("Flip Vertical", self)
            flip_v_action.triggered.connect(self._flip_vertical)
            menu.addAction(flip_v_action)

            menu.addSeparator()

            # Change Color submenu
            color_menu = menu.addMenu("Change Color")
            for i in range(16):
                color_data = INTELLIVISION_PALETTE[i]
                color_action = QAction(f"{color_data['name']} (#{i})", self)
                color_action.triggered.connect(lambda checked, idx=i: self._change_color(idx))
                color_menu.addAction(color_action)

        # Separator before code generation
        if has_card:
            menu.addSeparator()

        # Code generation submenu (only if card exists)
        if has_card:
            gen_menu = menu.addMenu("Generate Code")

            intybasic_visual_action = QAction("IntyBASIC (Visual)", self)
            intybasic_visual_action.triggered.connect(self._generate_intybasic_visual)
            gen_menu.addAction(intybasic_visual_action)

            intybasic_data_action = QAction("IntyBASIC (Data)", self)
            intybasic_data_action.triggered.connect(self._generate_intybasic_data)
            gen_menu.addAction(intybasic_data_action)

            gen_menu.addSeparator()

            mbcc_action = QAction("MBCC", self)
            mbcc_action.triggered.connect(self._generate_mbcc)
            gen_menu.addAction(mbcc_action)

            gen_menu.addSeparator()

            asm_action = QAction("Assembly (DECLE)", self)
            asm_action.triggered.connect(self._generate_asm)
            gen_menu.addAction(asm_action)

        menu.exec(event.globalPos())

    def _generate_intybasic_visual(self):
        """Generate IntyBASIC code for this card (visual format)"""
        if self.card is None:
            return

        # Get card data as binary strings
        binary_rows = self.card.to_binary_strings()

        # Convert to visual representation (1 -> X, 0 -> .)
        visual_rows = []
        for row in binary_rows:
            visual_row = row.replace('1', 'X').replace('0', '.')
            visual_rows.append(f'    "{visual_row}"')

        # Format as IntyBASIC BITMAP
        code = f"' GRAM Card #{self.slot} (slot {256 + self.slot})\n"
        code += f"BITMAP card_{self.slot}\n"
        code += "\n".join(visual_rows)
        code += "\nEND\n"

        self._show_code_dialog("IntyBASIC Code (Visual)", code)

    def _generate_intybasic_data(self):
        """Generate IntyBASIC code for this card (DATA format)"""
        if self.card is None:
            return

        # Get card data as 8 bytes
        data = self.card.to_bytes()

        # Format as IntyBASIC BITMAP with DATA
        code = f"' GRAM Card #{self.slot} (slot {256 + self.slot})\n"
        code += f"BITMAP card_{self.slot}\n"
        code += "    DATA "
        code += ", ".join(f"${byte:02X}" for byte in data)
        code += "\nEND\n"

        self._show_code_dialog("IntyBASIC Code (Data)", code)

    def _generate_mbcc(self):
        """Generate MBCC code for this card"""
        if self.card is None:
            return

        # Get card data as binary strings
        binary_rows = self.card.to_binary_strings()

        # Convert to visual representation (1 -> #, 0 -> .)
        visual_rows = []
        for row in binary_rows:
            visual_row = row.replace('1', '#').replace('0', '.')
            visual_rows.append(f'            "{visual_row}"')

        # Format as MBCC SBITMAP
        code = f"// GRAM Card #{self.slot} (slot {256 + self.slot})\n"
        code += f"const U16 card_{self.slot} = SBITMAP(\n"
        code += ",\n".join(visual_rows)
        code += ");\n"

        self._show_code_dialog("MBCC Code", code)

    def _generate_asm(self):
        """Generate Assembly DECLE code for this card"""
        if self.card is None:
            return

        # Get card data as 8 bytes
        data = self.card.to_bytes()

        # Pack bytes into 16-bit DECLEs (4 words for 8 bytes)
        # Intellivision is little-endian: low byte first
        code = f"; GRAM Card #{self.slot} (slot {256 + self.slot})\n"
        code += f"card_{self.slot}:\n"

        for i in range(0, 8, 2):
            low_byte = data[i]
            high_byte = data[i + 1] if i + 1 < 8 else 0
            decle = (high_byte << 8) | low_byte
            code += f"    DECLE ${decle:04X}    ; rows {i}-{i+1}\n"

        self._show_code_dialog("Assembly Code", code)

    def _show_code_dialog(self, title: str, code: str):
        """Show generated code in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(500, 300)

        layout = QVBoxLayout(dialog)

        # Code display
        text_edit = QTextEdit()
        text_edit.setPlainText(code)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier", 10))
        layout.addWidget(text_edit)

        # Copy button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(code))
        layout.addWidget(copy_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

    def _copy_card(self):
        """Copy this card to clipboard"""
        if self.card is not None and self.parent_grid:
            self.parent_grid.copy_card(self.card)

    def _paste_card(self):
        """Paste card from clipboard to this slot"""
        if self.parent_grid:
            self.parent_grid.paste_card(self.slot)

    def _clear_card(self):
        """Clear this card"""
        if self.card is not None and self.parent_grid and self.parent_grid.main_window:
            # Use undo command
            from telligram.gui.main_window import ClearCardCommand
            command = ClearCardCommand(self.parent_grid.main_window, self.slot)
            self.parent_grid.main_window.undo_stack.push(command)

    def _flip_horizontal(self):
        """Flip this card horizontally"""
        if self.card is not None and self.parent_grid and self.parent_grid.main_window:
            # Use undo command
            from telligram.gui.main_window import FlipHorizontalCommand
            command = FlipHorizontalCommand(self.parent_grid.main_window, self.slot)
            self.parent_grid.main_window.undo_stack.push(command)

    def _flip_vertical(self):
        """Flip this card vertically"""
        if self.card is not None and self.parent_grid and self.parent_grid.main_window:
            # Use undo command
            from telligram.gui.main_window import FlipVerticalCommand
            command = FlipVerticalCommand(self.parent_grid.main_window, self.slot)
            self.parent_grid.main_window.undo_stack.push(command)

    def _change_color(self, color_index: int):
        """Change this card's color"""
        if self.card is not None and self.parent_grid and self.parent_grid.main_window:
            old_color = self.card.color if hasattr(self.card, 'color') else 7
            if old_color != color_index:
                # Use undo command
                from telligram.gui.main_window import ChangeCardColorCommand
                command = ChangeCardColorCommand(self.parent_grid.main_window, self.slot, old_color, color_index)
                self.parent_grid.main_window.undo_stack.push(command)


class CardGridWidget(QWidget):
    """Grid widget showing all 64 GRAM cards"""

    card_selected = Signal(int)  # Emits slot number when card selected

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.project = None
        self.thumbnails = []
        self.current_slot = 0
        self._card_clipboard = None  # Clipboard for copy/paste

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        layout = QGridLayout(self)
        layout.setSpacing(4)

        # Create 64 thumbnails in 8×8 grid
        for i in range(64):
            thumb = CardThumbnail(i, parent_grid=self)
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

    def has_clipboard_data(self) -> bool:
        """Check if clipboard has card data"""
        return self._card_clipboard is not None

    def copy_card(self, card: GramCard):
        """Copy card data to clipboard"""
        if card is not None:
            # Store card data as bytes
            self._card_clipboard = card.to_bytes()

    def paste_card(self, slot: int):
        """Paste card from clipboard to specified slot"""
        if self._card_clipboard is None or self.project is None:
            return

        # Use undo command if main_window is available
        if self.main_window:
            from telligram.gui.main_window import PasteCardCommand
            command = PasteCardCommand(self.main_window, slot, self._card_clipboard)
            self.main_window.undo_stack.push(command)
        else:
            # Fallback for when main_window is not set
            new_card = GramCard(data=self._card_clipboard)
            self.project.set_card(slot, new_card)
            self.thumbnails[slot].set_card(new_card)
            self.select_card(slot)
            self.card_selected.emit(slot)
