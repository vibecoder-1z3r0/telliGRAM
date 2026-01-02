"""Version information for telliGRAM."""
import tomllib
from pathlib import Path

def get_version() -> str:
    """Get version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)
            return pyproject["project"]["version"]
    except Exception:
        # Fallback if pyproject.toml can't be read
        return "0.1.0-alpha"

__version__ = get_version()
