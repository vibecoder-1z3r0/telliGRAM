#!/usr/bin/env python3
"""Absolute minimum Qt test - no custom widgets at all"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt

class MinWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Qt Test")
        self.setMinimumSize(400, 300)

        label = QLabel("If you see this, basic Qt works on your WSL")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)

    print("Creating window...")
    window = MinWindow()

    print("Showing window...")
    window.show()

    print("Starting event loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
