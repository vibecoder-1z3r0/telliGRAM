"""Test configuration and fixtures"""
import pytest


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for GUI tests"""
    # Import only when needed (for GUI tests)
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    except ImportError:
        # Skip if PySide6 not properly installed
        pytest.skip("PySide6 not available")
