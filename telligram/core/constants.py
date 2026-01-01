"""Intellivision STIC constants and color palette definitions"""

# Intellivision Color Palette (jzIntv accurate colors)
# Standard 16-color STIC palette with RGB hex values from jzIntv emulator
INTELLIVISION_PALETTE = [
    # Index 0-7: Primary palette
    {"index": 0, "name": "Black", "hex": "#0C0005", "rgb": (12, 0, 5)},
    {"index": 1, "name": "Blue", "hex": "#002DFF", "rgb": (0, 45, 255)},
    {"index": 2, "name": "Red", "hex": "#FF3E00", "rgb": (255, 62, 0)},
    {"index": 3, "name": "Tan", "hex": "#C9CFAB", "rgb": (201, 207, 171)},
    {"index": 4, "name": "Dark Green", "hex": "#386B3F", "rgb": (56, 107, 63)},
    {"index": 5, "name": "Green", "hex": "#00A756", "rgb": (0, 167, 86)},
    {"index": 6, "name": "Yellow", "hex": "#FAEB27", "rgb": (250, 235, 39)},
    {"index": 7, "name": "White", "hex": "#FCFFFF", "rgb": (252, 255, 255)},

    # Index 8-15: Extended palette
    {"index": 8, "name": "Gray", "hex": "#A7A8A8", "rgb": (167, 168, 168)},
    {"index": 9, "name": "Cyan", "hex": "#5ACBFF", "rgb": (90, 203, 255)},
    {"index": 10, "name": "Orange", "hex": "#FFA048", "rgb": (255, 160, 72)},
    {"index": 11, "name": "Brown", "hex": "#BD8438", "rgb": (189, 132, 56)},
    {"index": 12, "name": "Pink", "hex": "#FF3276", "rgb": (255, 50, 118)},
    {"index": 13, "name": "Light Blue", "hex": "#5EB5FF", "rgb": (94, 181, 255)},
    {"index": 14, "name": "Yellow-Green", "hex": "#C3D959", "rgb": (195, 217, 89)},
    {"index": 15, "name": "Purple", "hex": "#C45CEC", "rgb": (196, 92, 236)},
]

# Default card color (White)
DEFAULT_CARD_COLOR = 7

def get_color_hex(index: int) -> str:
    """Get hex color string for a palette index (0-15)"""
    if 0 <= index < len(INTELLIVISION_PALETTE):
        return INTELLIVISION_PALETTE[index]["hex"]
    return INTELLIVISION_PALETTE[DEFAULT_CARD_COLOR]["hex"]

def get_color_rgb(index: int) -> tuple:
    """Get RGB tuple for a palette index (0-15)"""
    if 0 <= index < len(INTELLIVISION_PALETTE):
        return INTELLIVISION_PALETTE[index]["rgb"]
    return INTELLIVISION_PALETTE[DEFAULT_CARD_COLOR]["rgb"]

def get_color_name(index: int) -> str:
    """Get color name for a palette index (0-15)"""
    if 0 <= index < len(INTELLIVISION_PALETTE):
        return INTELLIVISION_PALETTE[index]["name"]
    return "Unknown"
