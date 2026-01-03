"""
Export Dialog - Unified dialog for exporting cards, animations, and GRAM sets.

Provides a dropdown for selecting export format and a text area for copying
the generated code.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTextEdit, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ExportDialog(QDialog):
    """Dialog for exporting code with format selection and copy/paste support."""

    def __init__(self, title, generator_func, parent=None):
        """
        Initialize export dialog.

        Args:
            title: Dialog window title
            generator_func: Function(format_key) -> str that generates code
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(700, 500)

        self.generator_func = generator_func

        # Main layout
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(f"<h2>{title}</h2>")
        layout.addWidget(title_label)

        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))

        self.format_combo = QComboBox()
        self.format_combo.addItem("IntyBASIC (Visual)", "intybasic_visual")
        self.format_combo.addItem("IntyBASIC (Data)", "intybasic_data")
        self.format_combo.addItem("MBCC", "mbcc")
        self.format_combo.addItem("Assembly (DECLE)", "asm")
        self.format_combo.currentIndexChanged.connect(self._update_code)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()

        layout.addLayout(format_layout)

        # Code text area
        code_label = QLabel("Generated Code:")
        layout.addWidget(code_label)

        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setFont(QFont("Courier New", 10))
        self.code_text.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.code_text)

        # Buttons
        button_layout = QHBoxLayout()

        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_btn)

        save_btn = QPushButton("Save to File...")
        save_btn.clicked.connect(self._save_to_file)
        button_layout.addWidget(save_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Generate initial code
        self._update_code()

    def _update_code(self):
        """Update code text based on selected format"""
        format_key = self.format_combo.currentData()
        code = self.generator_func(format_key)
        self.code_text.setPlainText(code)

    def _copy_to_clipboard(self):
        """Copy code to clipboard"""
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.code_text.toPlainText())

        # Show brief confirmation
        QMessageBox.information(
            self,
            "Copied",
            "Code copied to clipboard!",
            QMessageBox.Ok
        )

    def _save_to_file(self):
        """Save code to file"""
        format_key = self.format_combo.currentData()

        # Determine file filter based on format
        filters = {
            "intybasic_visual": "IntyBASIC Source (*.bas);;All Files (*)",
            "intybasic_data": "IntyBASIC Source (*.bas);;All Files (*)",
            "mbcc": "C Header (*.h);;C Source (*.c);;All Files (*)",
            "asm": "Assembly Source (*.asm);;All Files (*)"
        }

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export",
            "",
            filters.get(format_key, "All Files (*)")
        )

        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                f.write(self.code_text.toPlainText())

            QMessageBox.information(
                self,
                "Success",
                f"Code saved to:\n{filename}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file:\n{str(e)}"
            )
