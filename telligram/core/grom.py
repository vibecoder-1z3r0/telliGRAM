"""
GROM (Graphics ROM) data module.

Provides access to the 256 built-in Intellivision character graphics.
Cards 0-94 correspond to ASCII characters 32-126.
Cards 95-255 are extended graphics (system-specific).

GROM data is loaded from GROM.json if available, otherwise uses built-in defaults.
"""

from typing import List, Optional
import json
from pathlib import Path


class GromData:
    """
    GROM character data access.

    Provides the 256 built-in Intellivision GROM characters.
    Each character is 8x8 pixels (8 bytes, 1 byte per row).
    """

    def __init__(self, grom_json_path: Optional[Path] = None):
        """
        Initialize GROM data.

        Args:
            grom_json_path: Optional path to GROM.json file. If not provided,
                          looks for GROM.json in current directory, then uses built-in defaults.
        """
        self._labels = {}  # Custom labels from GROM.json
        self._data = self._load_grom_data(grom_json_path)

    @property
    def card_count(self) -> int:
        """Total number of GROM cards"""
        return 256

    def get_card(self, index: int) -> List[int]:
        """
        Get GROM card data by index (0-255).

        Args:
            index: GROM card number (0-255)

        Returns:
            List of 8 bytes representing the 8x8 character

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= self.card_count:
            raise IndexError(f"GROM card index {index} out of range (0-255)")
        return self._data[index]

    def ascii_to_grom(self, char: str) -> int:
        """
        Convert ASCII character to GROM card number.

        Formula: GROM = ASCII - 32

        Args:
            char: Single ASCII character

        Returns:
            GROM card number
        """
        return ord(char) - 32

    def grom_to_ascii(self, card_num: int) -> str:
        """
        Convert GROM card number to ASCII character.

        Formula: ASCII = GROM + 32

        Args:
            card_num: GROM card number (0-94 for ASCII range)

        Returns:
            ASCII character
        """
        return chr(card_num + 32)

    def get_card_by_ascii(self, char: str) -> List[int]:
        """
        Get GROM card data by ASCII character.

        Args:
            char: Single ASCII character

        Returns:
            List of 8 bytes representing the character
        """
        card_num = self.ascii_to_grom(char)
        return self.get_card(card_num)

    def get_label(self, card_num: int) -> str:
        """
        Get human-readable label for GROM card.

        Args:
            card_num: GROM card number (0-255)

        Returns:
            Custom label string, or empty string if no label defined
        """
        return self._labels.get(card_num, "")

    def is_ascii(self, card_num: int) -> bool:
        """
        Check if GROM card is in ASCII range.

        Args:
            card_num: GROM card number

        Returns:
            True if card is ASCII (0-94), False if extended (95-255)
        """
        return 0 <= card_num <= 94

    def text_to_cards(self, text: str) -> List[int]:
        """
        Convert text string to list of GROM card numbers.

        Args:
            text: Text string to convert

        Returns:
            List of GROM card numbers
        """
        return [self.ascii_to_grom(char) for char in text]

    def _load_grom_data(self, grom_json_path: Optional[Path] = None) -> List[List[int]]:
        """
        Load GROM data from JSON file.

        JSON format: Object with card numbers as keys
        {
          "0": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
          "33": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00],
          ...
        }

        Args:
            grom_json_path: Path to GROM.json file (required)

        Returns:
            List of 256 cards, each card is a list of 8 bytes.
            Undefined cards are filled with blank data.

        Raises:
            FileNotFoundError: If GROM file doesn't exist
            ValueError: If GROM file format is invalid
        """
        if not grom_json_path:
            raise ValueError("GROM file path is required")

        if not grom_json_path.exists():
            raise FileNotFoundError(f"GROM file not found: {grom_json_path}")

        try:
            with open(grom_json_path, 'r') as f:
                data = json.load(f)

                if not isinstance(data, dict):
                    raise ValueError(f"Invalid GROM.json format: expected object with card numbers as keys")

                # Initialize all 256 cards as blank
                cards = [[0x00] * 8 for _ in range(256)]
                loaded_count = 0

                # Load defined cards
                for key, value in data.items():
                    # Validate key is numeric
                    try:
                        card_num = int(key)
                    except ValueError:
                        print(f"WARNING: Ignoring non-numeric card key: '{key}'")
                        continue

                    # Validate card number is in range
                    if card_num < 0 or card_num > 255:
                        print(f"WARNING: Ignoring out-of-bounds card number: {card_num} (must be 0-255)")
                        continue

                    # Handle both old (array) and new (object) formats
                    card_data = None
                    card_label = None

                    if isinstance(value, dict):
                        # New format: {"data": [...], "label": "..."}
                        card_data = value.get("data")
                        card_label = value.get("label")
                        if card_data is None:
                            print(f"WARNING: Ignoring card {card_num}: missing 'data' field")
                            continue
                    elif isinstance(value, list):
                        # Old format: [...]
                        card_data = value
                    else:
                        print(f"WARNING: Ignoring card {card_num}: value must be array or object")
                        continue

                    # Validate card data is a list of 8 bytes
                    if not isinstance(card_data, list):
                        print(f"WARNING: Ignoring card {card_num}: data must be an array")
                        continue

                    if len(card_data) != 8:
                        print(f"WARNING: Ignoring card {card_num}: expected 8 bytes, got {len(card_data)}")
                        continue

                    # Parse and validate each byte
                    parsed_bytes = []
                    valid = True
                    for i, byte_val in enumerate(card_data):
                        parsed = self._parse_byte(byte_val)
                        if parsed is None:
                            print(f"WARNING: Ignoring card {card_num}: invalid byte at index {i}: {byte_val}")
                            valid = False
                            break
                        parsed_bytes.append(parsed)

                    if not valid:
                        continue

                    # Load the card
                    cards[card_num] = parsed_bytes

                    # Store custom label if provided
                    if card_label:
                        self._labels[card_num] = card_label

                    loaded_count += 1

                return cards

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {grom_json_path}: {e}")

    def _parse_byte(self, value) -> Optional[int]:
        """
        Parse a byte value from various formats.

        Supports:
        - Integer: 24
        - Hex: "0x18" (4 chars: 0x + 2 hex digits), "$18" (2-3 chars: $ + 1-2 hex digits)
        - Binary: "0b00110011" (10 chars: 0b + 8 binary digits)
        - BITMAP: "00110011" (8 chars: '0'/_/./space = 0, else = 1)
        - Decimal string: "24"

        Args:
            value: Value to parse

        Returns:
            Integer 0-255, or None if invalid
        """
        # Integer - use as-is
        if isinstance(value, int):
            return value if 0 <= value <= 255 else None

        if not isinstance(value, str):
            return None

        # BITMAP format: exactly 8 characters
        # '0', '_', ' ', '.' = pixel OFF (0), everything else = pixel ON (1)
        if len(value) == 8:
            binary_str = "".join("0" if c in "0_. " else "1" for c in value)
            result = int(binary_str, 2)
            return result if 0 <= result <= 255 else None

        # Hex: 4 characters starting with "0x" or "0X"
        if len(value) == 4 and value.startswith(("0x", "0X")):
            try:
                result = int(value, 16)
                return result if 0 <= result <= 255 else None
            except ValueError:
                return None

        # Hex: 2-3 characters starting with "$" (assembly style)
        if value.startswith("$") and 2 <= len(value) <= 3:
            try:
                result = int(value[1:], 16)
                return result if 0 <= result <= 255 else None
            except ValueError:
                return None

        # Binary: 10 characters starting with "0b" or "0B"
        if len(value) == 10 and value.startswith(("0b", "0B")):
            try:
                result = int(value, 2)
                return result if 0 <= result <= 255 else None
            except ValueError:
                return None

        # Decimal string: anything else, try to parse as decimal
        try:
            result = int(value.strip())
            return result if 0 <= result <= 255 else None
        except ValueError:
            return None

    def _initialize_grom_data(self) -> List[List[int]]:
        """
        Initialize built-in GROM character bitmap data (fallback).

        Returns complete 256-card GROM set.
        Each card is 8 bytes (one byte per row).
        """
        # Initialize all 256 cards with placeholder data
        cards = []

        # Add ASCII characters (0-94, corresponding to ASCII 32-126)
        cards.extend(self._get_ascii_characters())

        # Add extended characters (95-255) - use empty for now
        for i in range(95, 256):
            cards.append([0x00] * 8)

        return cards

    def _get_ascii_characters(self) -> List[List[int]]:
        """
        Get bitmap data for ASCII GROM characters (cards 0-94).

        Based on standard Intellivision GROM ROM.
        """
        # This is a subset of actual GROM data
        # Cards are ordered: 0-94 = ASCII 32-126

        return [
            # Card 0: Space (ASCII 32)
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            # Card 1: ! (ASCII 33)
            [0x10, 0x10, 0x10, 0x10, 0x10, 0x00, 0x10, 0x00],
            # Card 2: " (ASCII 34)
            [0x28, 0x28, 0x28, 0x00, 0x00, 0x00, 0x00, 0x00],
            # Card 3: # (ASCII 35)
            [0x28, 0x28, 0x7C, 0x28, 0x7C, 0x28, 0x28, 0x00],
            # Card 4: $ (ASCII 36)
            [0x10, 0x3C, 0x50, 0x38, 0x14, 0x78, 0x10, 0x00],
            # Card 5: % (ASCII 37)
            [0x60, 0x64, 0x08, 0x10, 0x20, 0x4C, 0x0C, 0x00],
            # Card 6: & (ASCII 38)
            [0x20, 0x50, 0x50, 0x20, 0x54, 0x48, 0x34, 0x00],
            # Card 7: ' (ASCII 39)
            [0x10, 0x10, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00],
            # Card 8: ( (ASCII 40)
            [0x08, 0x10, 0x20, 0x20, 0x20, 0x10, 0x08, 0x00],
            # Card 9: ) (ASCII 41)
            [0x20, 0x10, 0x08, 0x08, 0x08, 0x10, 0x20, 0x00],
            # Card 10: * (ASCII 42)
            [0x00, 0x10, 0x54, 0x38, 0x54, 0x10, 0x00, 0x00],
            # Card 11: + (ASCII 43)
            [0x00, 0x10, 0x10, 0x7C, 0x10, 0x10, 0x00, 0x00],
            # Card 12: , (ASCII 44)
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x10, 0x20],
            # Card 13: - (ASCII 45)
            [0x00, 0x00, 0x00, 0x7C, 0x00, 0x00, 0x00, 0x00],
            # Card 14: . (ASCII 46)
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x10, 0x00],
            # Card 15: / (ASCII 47)
            [0x00, 0x04, 0x08, 0x10, 0x20, 0x40, 0x00, 0x00],
            # Card 16: 0 (ASCII 48)
            [0x18, 0x24, 0x42, 0x42, 0x42, 0x42, 0x24, 0x18],
            # Card 17: 1 (ASCII 49)
            [0x10, 0x30, 0x10, 0x10, 0x10, 0x10, 0x38, 0x00],
            # Card 18: 2 (ASCII 50)
            [0x38, 0x44, 0x04, 0x08, 0x10, 0x20, 0x7C, 0x00],
            # Card 19: 3 (ASCII 51)
            [0x38, 0x44, 0x04, 0x18, 0x04, 0x44, 0x38, 0x00],
            # Card 20: 4 (ASCII 52)
            [0x08, 0x18, 0x28, 0x48, 0x7C, 0x08, 0x08, 0x00],
            # Card 21: 5 (ASCII 53)
            [0x7C, 0x40, 0x78, 0x04, 0x04, 0x44, 0x38, 0x00],
            # Card 22: 6 (ASCII 54)
            [0x18, 0x20, 0x40, 0x78, 0x44, 0x44, 0x38, 0x00],
            # Card 23: 7 (ASCII 55)
            [0x7C, 0x04, 0x08, 0x10, 0x20, 0x20, 0x20, 0x00],
            # Card 24: 8 (ASCII 56)
            [0x38, 0x44, 0x44, 0x38, 0x44, 0x44, 0x38, 0x00],
            # Card 25: 9 (ASCII 57)
            [0x38, 0x44, 0x44, 0x3C, 0x04, 0x08, 0x30, 0x00],
            # Card 26: : (ASCII 58)
            [0x00, 0x00, 0x10, 0x00, 0x00, 0x10, 0x00, 0x00],
            # Card 27: ; (ASCII 59)
            [0x00, 0x00, 0x10, 0x00, 0x00, 0x10, 0x10, 0x20],
            # Card 28: < (ASCII 60)
            [0x04, 0x08, 0x10, 0x20, 0x10, 0x08, 0x04, 0x00],
            # Card 29: = (ASCII 61)
            [0x00, 0x00, 0x7C, 0x00, 0x7C, 0x00, 0x00, 0x00],
            # Card 30: > (ASCII 62)
            [0x20, 0x10, 0x08, 0x04, 0x08, 0x10, 0x20, 0x00],
            # Card 31: ? (ASCII 63)
            [0x38, 0x44, 0x04, 0x08, 0x10, 0x00, 0x10, 0x00],
            # Card 32: @ (ASCII 64)
            [0x38, 0x44, 0x5C, 0x54, 0x5C, 0x40, 0x38, 0x00],
            # Card 33: A (ASCII 65)
            [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00],
            # Card 34: B (ASCII 66)
            [0x78, 0x44, 0x44, 0x78, 0x44, 0x44, 0x78, 0x00],
            # Card 35: C (ASCII 67)
            [0x38, 0x44, 0x40, 0x40, 0x40, 0x44, 0x38, 0x00],
            # Card 36: D (ASCII 68)
            [0x78, 0x44, 0x44, 0x44, 0x44, 0x44, 0x78, 0x00],
            # Card 37: E (ASCII 69)
            [0x7C, 0x40, 0x40, 0x78, 0x40, 0x40, 0x7C, 0x00],
            # Card 38: F (ASCII 70)
            [0x7C, 0x40, 0x40, 0x78, 0x40, 0x40, 0x40, 0x00],
            # Card 39: G (ASCII 71)
            [0x38, 0x44, 0x40, 0x4C, 0x44, 0x44, 0x38, 0x00],
            # Card 40: H (ASCII 72)
            [0x44, 0x44, 0x44, 0x7C, 0x44, 0x44, 0x44, 0x00],
            # Card 41: I (ASCII 73)
            [0x38, 0x10, 0x10, 0x10, 0x10, 0x10, 0x38, 0x00],
            # Card 42: J (ASCII 74)
            [0x04, 0x04, 0x04, 0x04, 0x44, 0x44, 0x38, 0x00],
            # Card 43: K (ASCII 75)
            [0x44, 0x48, 0x50, 0x60, 0x50, 0x48, 0x44, 0x00],
            # Card 44: L (ASCII 76)
            [0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x7C, 0x00],
            # Card 45: M (ASCII 77)
            [0x44, 0x6C, 0x54, 0x44, 0x44, 0x44, 0x44, 0x00],
            # Card 46: N (ASCII 78)
            [0x44, 0x64, 0x54, 0x4C, 0x44, 0x44, 0x44, 0x00],
            # Card 47: O (ASCII 79)
            [0x38, 0x44, 0x44, 0x44, 0x44, 0x44, 0x38, 0x00],
            # Card 48: P (ASCII 80)
            [0x78, 0x44, 0x44, 0x78, 0x40, 0x40, 0x40, 0x00],
            # Card 49: Q (ASCII 81)
            [0x38, 0x44, 0x44, 0x44, 0x54, 0x48, 0x34, 0x00],
            # Card 50: R (ASCII 82)
            [0x78, 0x44, 0x44, 0x78, 0x50, 0x48, 0x44, 0x00],
            # Card 51: S (ASCII 83)
            [0x38, 0x44, 0x40, 0x38, 0x04, 0x44, 0x38, 0x00],
            # Card 52: T (ASCII 84)
            [0x7C, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00],
            # Card 53: U (ASCII 85)
            [0x44, 0x44, 0x44, 0x44, 0x44, 0x44, 0x38, 0x00],
            # Card 54: V (ASCII 86)
            [0x44, 0x44, 0x44, 0x44, 0x44, 0x28, 0x10, 0x00],
            # Card 55: W (ASCII 87)
            [0x44, 0x44, 0x44, 0x54, 0x54, 0x6C, 0x44, 0x00],
            # Card 56: X (ASCII 88)
            [0x44, 0x44, 0x28, 0x10, 0x28, 0x44, 0x44, 0x00],
            # Card 57: Y (ASCII 89)
            [0x44, 0x44, 0x28, 0x10, 0x10, 0x10, 0x10, 0x00],
            # Card 58: Z (ASCII 90)
            [0x7C, 0x04, 0x08, 0x10, 0x20, 0x40, 0x7C, 0x00],
            # Card 59: [ (ASCII 91)
            [0x38, 0x20, 0x20, 0x20, 0x20, 0x20, 0x38, 0x00],
            # Card 60: \ (ASCII 92)
            [0x00, 0x40, 0x20, 0x10, 0x08, 0x04, 0x00, 0x00],
            # Card 61: ] (ASCII 93)
            [0x38, 0x08, 0x08, 0x08, 0x08, 0x08, 0x38, 0x00],
            # Card 62: ^ (ASCII 94)
            [0x10, 0x28, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00],
            # Card 63: _ (ASCII 95)
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7C, 0x00],
            # Card 64: ` (ASCII 96)
            [0x20, 0x10, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00],
            # Card 65: a (ASCII 97)
            [0x00, 0x00, 0x38, 0x04, 0x3C, 0x44, 0x3C, 0x00],
            # Card 66: b (ASCII 98)
            [0x40, 0x40, 0x58, 0x64, 0x44, 0x44, 0x78, 0x00],
            # Card 67: c (ASCII 99)
            [0x00, 0x00, 0x38, 0x44, 0x40, 0x44, 0x38, 0x00],
            # Card 68: d (ASCII 100)
            [0x04, 0x04, 0x34, 0x4C, 0x44, 0x44, 0x3C, 0x00],
            # Card 69: e (ASCII 101)
            [0x00, 0x00, 0x38, 0x44, 0x7C, 0x40, 0x38, 0x00],
            # Card 70: f (ASCII 102)
            [0x18, 0x24, 0x20, 0x78, 0x20, 0x20, 0x20, 0x00],
            # Card 71: g (ASCII 103)
            [0x00, 0x00, 0x3C, 0x44, 0x44, 0x3C, 0x04, 0x38],
            # Card 72: h (ASCII 104)
            [0x40, 0x40, 0x58, 0x64, 0x44, 0x44, 0x44, 0x00],
            # Card 73: i (ASCII 105)
            [0x10, 0x00, 0x30, 0x10, 0x10, 0x10, 0x38, 0x00],
            # Card 74: j (ASCII 106)
            [0x08, 0x00, 0x18, 0x08, 0x08, 0x48, 0x48, 0x30],
            # Card 75: k (ASCII 107)
            [0x40, 0x40, 0x48, 0x50, 0x60, 0x50, 0x48, 0x00],
            # Card 76: l (ASCII 108)
            [0x30, 0x10, 0x10, 0x10, 0x10, 0x10, 0x38, 0x00],
            # Card 77: m (ASCII 109)
            [0x00, 0x00, 0x68, 0x54, 0x54, 0x54, 0x44, 0x00],
            # Card 78: n (ASCII 110)
            [0x00, 0x00, 0x58, 0x64, 0x44, 0x44, 0x44, 0x00],
            # Card 79: o (ASCII 111)
            [0x00, 0x00, 0x38, 0x44, 0x44, 0x44, 0x38, 0x00],
            # Card 80: p (ASCII 112)
            [0x00, 0x00, 0x78, 0x44, 0x44, 0x78, 0x40, 0x40],
            # Card 81: q (ASCII 113)
            [0x00, 0x00, 0x3C, 0x44, 0x44, 0x3C, 0x04, 0x04],
            # Card 82: r (ASCII 114)
            [0x00, 0x00, 0x58, 0x64, 0x40, 0x40, 0x40, 0x00],
            # Card 83: s (ASCII 115)
            [0x00, 0x00, 0x38, 0x40, 0x38, 0x04, 0x78, 0x00],
            # Card 84: t (ASCII 116)
            [0x20, 0x20, 0x78, 0x20, 0x20, 0x24, 0x18, 0x00],
            # Card 85: u (ASCII 117)
            [0x00, 0x00, 0x44, 0x44, 0x44, 0x4C, 0x34, 0x00],
            # Card 86: v (ASCII 118)
            [0x00, 0x00, 0x44, 0x44, 0x44, 0x28, 0x10, 0x00],
            # Card 87: w (ASCII 119)
            [0x00, 0x00, 0x44, 0x44, 0x54, 0x54, 0x28, 0x00],
            # Card 88: x (ASCII 120)
            [0x00, 0x00, 0x44, 0x28, 0x10, 0x28, 0x44, 0x00],
            # Card 89: y (ASCII 121)
            [0x00, 0x00, 0x44, 0x44, 0x44, 0x3C, 0x04, 0x38],
            # Card 90: z (ASCII 122)
            [0x00, 0x00, 0x7C, 0x08, 0x10, 0x20, 0x7C, 0x00],
            # Card 91: { (ASCII 123)
            [0x18, 0x20, 0x20, 0x40, 0x20, 0x20, 0x18, 0x00],
            # Card 92: | (ASCII 124)
            [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00],
            # Card 93: } (ASCII 125)
            [0x30, 0x08, 0x08, 0x04, 0x08, 0x08, 0x30, 0x00],
            # Card 94: ~ (ASCII 126)
            [0x00, 0x00, 0x24, 0x58, 0x00, 0x00, 0x00, 0x00],
        ]
