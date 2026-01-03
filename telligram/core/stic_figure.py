"""
STIC Figure module for complete Intellivision screen layouts.

STIC Figures represent full BACKTAB configurations including:
- 20×12 BACKTAB grid (240 tiles)
- Color Stack or FG/BG mode
- Border settings
- MOB configurations (future)
"""

from typing import List, Dict, Any, Optional


class SticFigure:
    """
    Complete STIC screen configuration.

    Stores BACKTAB layout, color settings, border configuration, and display mode.
    Designed for visual screen design and export to game code.
    """

    def __init__(
        self,
        name: str,
        mode: str = "color_stack"
    ):
        """
        Create new STIC figure.

        Args:
            name: Figure name
            mode: Display mode - "color_stack" or "fg_bg"

        Raises:
            ValueError: If mode is invalid
        """
        if mode not in ("color_stack", "fg_bg"):
            raise ValueError(f"Mode must be 'color_stack' or 'fg_bg', got '{mode}'")

        self.name = name
        self.mode = mode

        # Border settings
        self.border_visible = True
        self.border_color = 0  # Black
        self.show_left_border = True
        self.show_top_border = True

        # Color stack (used in color_stack mode)
        self.color_stack = [0, 1, 2, 3]  # Default: Black, Blue, Brown, Tan

        # BACKTAB data: 240 tiles (20 cols × 12 rows)
        # Each tile: {card, fg_color, bg_color, advance_stack}
        self._backtab: List[Dict[str, Any]] = []
        for row in range(12):
            for col in range(20):
                self._backtab.append({
                    "row": row,
                    "col": col,
                    "card": 0,
                    "fg_color": 7,
                    "bg_color": 0,  # Only used in fg_bg mode
                    "advance_stack": False  # Only used in color_stack mode
                })

    def get_tile(self, row: int, col: int) -> Dict[str, Any]:
        """
        Get tile data at position.

        Args:
            row: Row index (0-11)
            col: Column index (0-19)

        Returns:
            Tile data dictionary

        Raises:
            IndexError: If row/col out of range
        """
        if not (0 <= row < 12 and 0 <= col < 20):
            raise IndexError(f"Tile position out of range: ({row}, {col})")

        index = row * 20 + col
        return self._backtab[index]

    def set_tile(
        self,
        row: int,
        col: int,
        card: int,
        fg_color: int,
        bg_color: int = 0,
        advance_stack: bool = False
    ) -> None:
        """
        Set tile data at position.

        Args:
            row: Row index (0-11)
            col: Column index (0-19)
            card: Card number (0-319)
            fg_color: Foreground color (0-15)
            bg_color: Background color (0-15, fg_bg mode only)
            advance_stack: Advance color stack (color_stack mode only)

        Raises:
            IndexError: If row/col out of range
        """
        if not (0 <= row < 12 and 0 <= col < 20):
            raise IndexError(f"Tile position out of range: ({row}, {col})")

        index = row * 20 + col
        self._backtab[index] = {
            "row": row,
            "col": col,
            "card": card,
            "fg_color": fg_color,
            "bg_color": bg_color,
            "advance_stack": advance_stack
        }

    def get_all_tiles(self) -> List[Dict[str, Any]]:
        """
        Get all BACKTAB tiles.

        Returns:
            List of 240 tile dictionaries
        """
        return self._backtab.copy()

    def set_color_stack(self, slot0: int, slot1: int, slot2: int, slot3: int) -> None:
        """
        Set all color stack values.

        Args:
            slot0: Color stack slot 0 (0-15)
            slot1: Color stack slot 1 (0-15)
            slot2: Color stack slot 2 (0-15)
            slot3: Color stack slot 3 (0-15)
        """
        self.color_stack = [slot0, slot1, slot2, slot3]

    def set_border(
        self,
        visible: bool = True,
        color: int = 0,
        show_left: bool = True,
        show_top: bool = True
    ) -> None:
        """
        Set border configuration.

        Args:
            visible: Whether border is visible
            color: Border color (0-15)
            show_left: Show left border (8px)
            show_top: Show top border (8px)
        """
        self.border_visible = visible
        self.border_color = color
        self.show_left_border = show_left
        self.show_top_border = show_top

    def to_dict(self) -> Dict[str, Any]:
        """
        Export figure to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "mode": self.mode,
            "border": {
                "visible": self.border_visible,
                "color": self.border_color,
                "show_left": self.show_left_border,
                "show_top": self.show_top_border
            },
            "color_stack": self.color_stack.copy(),
            "backtab": self._backtab.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SticFigure':
        """
        Create STIC figure from dictionary.

        Args:
            data: Dictionary from to_dict()

        Returns:
            SticFigure instance
        """
        figure = cls(
            name=data["name"],
            mode=data.get("mode", "color_stack")
        )

        # Load border settings
        if "border" in data:
            border = data["border"]
            figure.border_visible = border.get("visible", True)
            figure.border_color = border.get("color", 0)
            figure.show_left_border = border.get("show_left", True)
            figure.show_top_border = border.get("show_top", True)

        # Load color stack
        if "color_stack" in data:
            figure.color_stack = data["color_stack"].copy()

        # Load BACKTAB data
        if "backtab" in data:
            figure._backtab = data["backtab"].copy()

        return figure

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"SticFigure(name='{self.name}', mode='{self.mode}')"
