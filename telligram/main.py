"""
Main entry point for telliGRAM application
"""
import sys
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication
from telligram.gui.main_window import MainWindow


def main():
    """Launch telliGRAM GUI application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="telliGRAM - Intellivision GRAM Card Creator")
    parser.add_argument(
        "--grom",
        type=str,
        help="Path to GROM.json file (enables GROM Viewer tab)"
    )
    args = parser.parse_args()

    # Convert GROM path to Path object if provided
    grom_path = Path(args.grom) if args.grom else None

    app = QApplication(sys.argv)
    app.setApplicationName("telliGRAM")
    app.setOrganizationName("Vibe-Coder")

    window = MainWindow(grom_path=grom_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
