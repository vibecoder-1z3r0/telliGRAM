#!/usr/bin/env python3
"""Debug startup to find where it hangs"""
import sys

print("1. Importing PySide6...")
from PySide6.QtWidgets import QApplication
print("   ✓ PySide6 imported")

print("2. Creating QApplication...")
app = QApplication(sys.argv)
print("   ✓ QApplication created")

print("3. Setting app properties...")
app.setApplicationName("telliGRAM")
app.setOrganizationName("Vibe-Coder")
print("   ✓ Properties set")

print("4. Importing MainWindow...")
from telligram.gui.main_window import MainWindow
print("   ✓ MainWindow imported")

print("5. Creating MainWindow instance...")
window = MainWindow()
print("   ✓ MainWindow created")

print("6. Showing window...")
window.show()
print("   ✓ Window shown")

print("7. Starting event loop...")
sys.exit(app.exec())
