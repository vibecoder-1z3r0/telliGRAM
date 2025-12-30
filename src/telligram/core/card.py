"""GRAM Card data model"""
from typing import List, Optional, Dict, Any


class GramCard:
    """
    Represents a single 8×8 GRAM card

    GRAM cards are 1-bit graphics (pixel on/off only).
    Each card is 8 bytes (one byte per row).
    """

    WIDTH = 8
    HEIGHT = 8

    def __init__(self, data: Optional[List[int]] = None):
        """
        Initialize GRAM card

        Args:
            data: Optional list of 8 bytes (one per row), each 0-255

        Raises:
            ValueError: If data is not 8 bytes or contains invalid values
        """
        if data is None:
            self._data = [0] * self.HEIGHT
        else:
            if len(data) != self.HEIGHT:
                raise ValueError(f"Card data must be {self.HEIGHT} bytes, got {len(data)}")

            # Validate each byte is 0-255
            for i, byte in enumerate(data):
                if not isinstance(byte, int) or not (0 <= byte <= 255):
                    raise ValueError(f"Byte {i} must be 0-255, got {byte}")

            self._data = list(data)

        self.label = ""

    @property
    def width(self) -> int:
        """Card width in pixels"""
        return self.WIDTH

    @property
    def height(self) -> int:
        """Card height in pixels"""
        return self.HEIGHT

    def get_pixel(self, x: int, y: int) -> int:
        """
        Get pixel value at (x, y)

        Args:
            x: Column (0-7, left to right)
            y: Row (0-7, top to bottom)

        Returns:
            0 or 1

        Raises:
            IndexError: If coordinates out of bounds
        """
        if not (0 <= x < self.WIDTH and 0 <= y < self.HEIGHT):
            raise IndexError(f"Pixel coordinates ({x}, {y}) out of bounds (0-7, 0-7)")

        byte = self._data[y]
        bit = 7 - x  # MSB (bit 7) is leftmost pixel (x=0)
        return (byte >> bit) & 1

    def set_pixel(self, x: int, y: int, value: int) -> None:
        """
        Set pixel value at (x, y)

        Args:
            x: Column (0-7)
            y: Row (0-7)
            value: 0 or 1

        Raises:
            IndexError: If coordinates out of bounds
        """
        if not (0 <= x < self.WIDTH and 0 <= y < self.HEIGHT):
            raise IndexError(f"Pixel coordinates ({x}, {y}) out of bounds (0-7, 0-7)")

        bit = 7 - x
        if value:
            self._data[y] |= (1 << bit)  # Set bit
        else:
            self._data[y] &= ~(1 << bit)  # Clear bit

    def to_bytes(self) -> List[int]:
        """Export card as list of 8 bytes"""
        return list(self._data)

    def to_binary_strings(self) -> List[str]:
        """
        Export as list of binary strings

        Returns:
            List of 8 strings, each 8 characters (e.g., "11110000")
        """
        return [format(byte, '08b') for byte in self._data]

    def to_hex_strings(self) -> List[str]:
        """
        Export as list of hex strings

        Returns:
            List of 8 strings, each 2 characters (e.g., "FF")
        """
        return [format(byte, '02X') for byte in self._data]

    def to_dict(self) -> Dict[str, Any]:
        """
        Export as dictionary for JSON serialization

        Returns:
            Dict with 'label' and 'data' keys
        """
        return {
            "label": self.label,
            "data": self.to_bytes()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GramCard':
        """
        Create card from dictionary

        Args:
            data: Dict with 'label' and 'data' keys

        Returns:
            New GramCard instance
        """
        card = cls(data["data"])
        card.label = data.get("label", "")
        return card

    def flip_horizontal(self) -> None:
        """Flip card horizontally (mirror left-right)"""
        for i in range(self.HEIGHT):
            # Reverse bits in each byte
            byte = self._data[i]
            reversed_byte = 0
            for bit in range(8):
                if byte & (1 << bit):
                    reversed_byte |= (1 << (7 - bit))
            self._data[i] = reversed_byte

    def flip_vertical(self) -> None:
        """Flip card vertically (mirror top-bottom)"""
        self._data.reverse()

    def clear(self) -> None:
        """Clear all pixels (set to 0)"""
        self._data = [0] * self.HEIGHT

    def invert(self) -> None:
        """Invert all pixels (0→1, 1→0)"""
        self._data = [byte ^ 0xFF for byte in self._data]

    def is_empty(self) -> bool:
        """
        Check if card is empty (all pixels off)

        Returns:
            True if all pixels are 0
        """
        return all(byte == 0 for byte in self._data)

    def __eq__(self, other: object) -> bool:
        """Check equality with another card"""
        if not isinstance(other, GramCard):
            return False
        return self._data == other._data

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"GramCard(label='{self.label}', data={self._data})"
