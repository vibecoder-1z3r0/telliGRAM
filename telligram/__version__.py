"""Version information for telliGRAM."""

import sys
from pathlib import Path


def get_version() -> str:
    """Get version from pyproject.toml"""
    try:
        # Python 3.11+ has tomllib built-in
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            # For older Python versions, use tomli
            import tomli as tomllib

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)
            return pyproject["project"]["version"]
    except Exception:
        # Fallback if pyproject.toml can't be read or tomli not installed
        return "0.1.0-alpha"


__version__ = get_version()
