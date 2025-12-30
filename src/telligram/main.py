"""
Main entry point for telliGRAM application
"""
import sys
from PySide6.QtWidgets import QApplication
from telligram.gui.main_window import MainWindow


def main():
    """Launch telliGRAM GUI application"""
    app = QApplication(sys.argv)
    app.setApplicationName("telliGRAM")
    app.setOrganizationName("Vibe-Coder")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
