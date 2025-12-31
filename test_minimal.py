#!/usr/bin/env python3
"""Minimal Qt test to isolate the issue"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor

class SimpleWidget(QWidget):
    """Simple widget with custom painting"""
    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0, 0, 100, 100, QColor(255, 0, 0))

class MinimalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Test")
        self.setMinimumSize(400, 300)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Test 1: Simple label
        layout.addWidget(QLabel("Test 1: Label works"))

        # Test 2: Custom painted widget
        layout.addWidget(QLabel("Test 2: Custom painting below"))
        layout.addWidget(SimpleWidget())

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)

    print("Creating window...")
    window = MinimalWindow()

    print("Showing window...")
    window.show()

    print("Starting event loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
