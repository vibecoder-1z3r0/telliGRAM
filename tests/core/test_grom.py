"""
Tests for GROM (Graphics ROM) data module.

GROM contains 256 built-in characters (0-255) that are always available.
Cards 0-94 map to ASCII 32-126.
"""

import pytest
import json
import tempfile
from pathlib import Path
from telligram.core.grom import GromData


class TestGromData:
    """Test GROM data access"""

    def test_grom_has_256_cards(self):
        """Should have exactly 256 GROM cards"""
        grom = GromData()
        assert grom.card_count == 256

    def test_get_card_by_index(self):
        """Should get GROM card by index (0-255)"""
        grom = GromData()
        # Get space character (card 0, ASCII 32)
        card = grom.get_card(0)
        assert card is not None
        assert len(card) == 8  # 8 bytes per card

    def test_get_card_out_of_range_raises_error(self):
        """Should raise error for invalid card index"""
        grom = GromData()
        with pytest.raises(IndexError):
            grom.get_card(256)
        with pytest.raises(IndexError):
            grom.get_card(-1)

    def test_ascii_to_grom_conversion(self):
        """Should convert ASCII character to GROM card number"""
        grom = GromData()
        # 'A' is ASCII 65, GROM card 33
        assert grom.ascii_to_grom('A') == 33
        # '0' is ASCII 48, GROM card 16
        assert grom.ascii_to_grom('0') == 16
        # Space is ASCII 32, GROM card 0
        assert grom.ascii_to_grom(' ') == 0

    def test_grom_to_ascii_conversion(self):
        """Should convert GROM card number to ASCII character"""
        grom = GromData()
        assert grom.grom_to_ascii(33) == 'A'
        assert grom.grom_to_ascii(16) == '0'
        assert grom.grom_to_ascii(0) == ' '

    def test_get_card_by_ascii(self):
        """Should get GROM card data by ASCII character"""
        grom = GromData()
        card_a = grom.get_card_by_ascii('A')
        card_33 = grom.get_card(33)
        assert card_a == card_33

    def test_get_card_label(self):
        """Should get label for GROM card"""
        grom = GromData()
        # ASCII characters should return their character
        assert grom.get_label(0) == "' '"
        assert grom.get_label(33) == "'A'"
        assert grom.get_label(16) == "'0'"
        # Extended characters should return description
        assert grom.get_label(95) != ""

    def test_is_ascii_card(self):
        """Should identify ASCII vs extended GROM cards"""
        grom = GromData()
        assert grom.is_ascii(0) is True
        assert grom.is_ascii(94) is True
        assert grom.is_ascii(95) is False
        assert grom.is_ascii(255) is False


class TestGromCardData:
    """Test actual GROM character bitmap data"""

    def test_space_is_empty(self):
        """Space character (card 0) should be all zeros"""
        grom = GromData()
        space = grom.get_card(0)
        assert all(byte == 0 for byte in space)

    def test_letter_a_has_correct_bitmap(self):
        """Letter 'A' should match expected bitmap"""
        grom = GromData()
        card_a = grom.get_card(33)  # 'A' is GROM card 33
        # Based on GROM_LAYOUT.md documentation:
        # ..XXX... = 0x18
        # .X...X.. = 0x24
        # X.....X. = 0x42
        # X.....X. = 0x42
        # XXXXXXX. = 0x7E
        # X.....X. = 0x42
        # X.....X. = 0x42
        # ........ = 0x00
        expected = [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        assert list(card_a) == expected

    def test_number_zero_has_correct_bitmap(self):
        """Number '0' should match expected bitmap"""
        grom = GromData()
        card_0 = grom.get_card(16)  # '0' is GROM card 16
        # Based on GROM_LAYOUT.md documentation
        expected = [0x18, 0x24, 0x42, 0x42, 0x42, 0x42, 0x24, 0x18]
        assert list(card_0) == expected


class TestGromStringConversion:
    """Test converting text strings to GROM card sequences"""

    def test_text_to_grom_cards(self):
        """Should convert text string to GROM card numbers"""
        grom = GromData()
        cards = grom.text_to_cards("HELLO")
        # H=40, E=37, L=44, L=44, O=47
        assert cards == [40, 37, 44, 44, 47]

    def test_text_to_grom_with_numbers(self):
        """Should convert numbers in text"""
        grom = GromData()
        cards = grom.text_to_cards("SCORE: 100")
        # S=51, C=35, O=47, R=50, E=37, :=26, space=0, 1=17, 0=16, 0=16
        assert cards == [51, 35, 47, 50, 37, 26, 0, 17, 16, 16]

    def test_empty_string(self):
        """Should handle empty string"""
        grom = GromData()
        assert grom.text_to_cards("") == []


class TestGromByteParsing:
    """Test flexible byte parsing in GROM.json"""

    @pytest.fixture
    def grom_with_test_file(self):
        """Create a temporary GROM file for testing"""
        def _create_grom(data):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f)
                temp_path = Path(f.name)
            grom = GromData(temp_path)
            temp_path.unlink()  # Clean up
            return grom
        return _create_grom

    def test_parse_decimal_int(self, grom_with_test_file):
        """Should parse decimal integers"""
        grom = grom_with_test_file({
            "0": [24, 36, 66, 66, 126, 66, 66, 0]
        })
        card = grom.get_card(0)
        assert card == [24, 36, 66, 66, 126, 66, 66, 0]

    def test_parse_hex_with_prefix(self, grom_with_test_file):
        """Should parse hex strings with 0x prefix"""
        grom = grom_with_test_file({
            "0": ["0x18", "0x24", "0x42", "0x42", "0x7E", "0x42", "0x42", "0x00"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_binary_with_prefix(self, grom_with_test_file):
        """Should parse binary strings with 0b prefix"""
        grom = grom_with_test_file({
            "0": ["0b00011000", "0b00100100", "0b01000010", "0b01000010",
                  "0b01111110", "0b01000010", "0b01000010", "0b00000000"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_binary_without_prefix(self, grom_with_test_file):
        """Should parse binary strings without prefix (exactly 8 chars)"""
        grom = grom_with_test_file({
            "0": ["00011000", "00100100", "01000010", "01000010",
                  "01111110", "01000010", "01000010", "00000000"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_decimal_string(self, grom_with_test_file):
        """Should parse decimal strings"""
        grom = grom_with_test_file({
            "0": ["24", "36", "66", "66", "126", "66", "66", "0"]
        })
        card = grom.get_card(0)
        assert card == [24, 36, 66, 66, 126, 66, 66, 0]

    def test_parse_mixed_formats(self, grom_with_test_file):
        """Should handle mixed formats in same card"""
        grom = grom_with_test_file({
            "0": [24, "0x24", "42", "0b01000010", "0x7E", "0x42", 66, "0x00"]
        })
        card = grom.get_card(0)
        # Mix of integer, hex, decimal string, binary
        assert card == [24, 0x24, 42, 0x42, 0x7E, 0x42, 66, 0x00]

    def test_sparse_cards(self, grom_with_test_file):
        """Should fill undefined cards with zeros"""
        grom = grom_with_test_file({
            "0": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00],
            "255": [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        })
        # Card 0 should be defined
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        # Card 1 should be blank (not defined)
        assert grom.get_card(1) == [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        # Card 255 should be defined
        assert grom.get_card(255) == [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    def test_invalid_byte_value_ignored(self, grom_with_test_file, capsys):
        """Should ignore invalid byte values with warning"""
        grom = grom_with_test_file({
            "0": [24, "invalid", 66, 66, 126, 66, 66, 0],  # Invalid byte
            "1": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]  # Valid card
        })
        # Card 0 should be blank (invalid data)
        assert grom.get_card(0) == [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        # Card 1 should be loaded
        assert grom.get_card(1) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        # Check warning was printed
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "card 0" in captured.out.lower()

    def test_out_of_bounds_card_ignored(self, grom_with_test_file, capsys):
        """Should ignore out-of-bounds card numbers"""
        grom = grom_with_test_file({
            "-1": [24, 36, 66, 66, 126, 66, 66, 0],  # Negative
            "256": [24, 36, 66, 66, 126, 66, 66, 0],  # Too large
            "0": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]  # Valid
        })
        # Only card 0 should be loaded
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        # Check warnings
        captured = capsys.readouterr()
        assert "out-of-bounds" in captured.out.lower()

    def test_non_numeric_key_ignored(self, grom_with_test_file, capsys):
        """Should ignore invalid keys"""
        grom = grom_with_test_file({
            "foo": [24, 36, 66, 66, 126, 66, 66, 0],  # Invalid key
            "0": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]  # Valid
        })
        # Only card 0 should be loaded
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        # Check warning
        captured = capsys.readouterr()
        assert "invalid card key" in captured.out.lower()

    def test_parse_visual_format_with_dots(self, grom_with_test_file):
        """Should parse visual format with dots (.) as 0"""
        # 0x18=00011000, 0x24=00100100, 0x42=01000010, 0x7E=01111110, 0x00=00000000
        grom = grom_with_test_file({
            "0": ["...XX...", "..X..X..", ".X....X.", ".X....X.",
                  ".XXXXXX.", ".X....X.", ".X....X.", "........"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_visual_format_with_zeros(self, grom_with_test_file):
        """Should parse visual format with zeros (0) as 0"""
        grom = grom_with_test_file({
            "0": ["000XX000", "00X00X00", "0X0000X0", "0X0000X0",
                  "0XXXXXX0", "0X0000X0", "0X0000X0", "00000000"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_visual_format_with_underscores(self, grom_with_test_file):
        """Should parse visual format with underscores (_) as 0"""
        grom = grom_with_test_file({
            "0": ["___XX___", "__X__X__", "_X____X_", "_X____X_",
                  "_XXXXXX_", "_X____X_", "_X____X_", "________"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_visual_format_with_spaces(self, grom_with_test_file):
        """Should parse visual format with spaces as 0"""
        grom = grom_with_test_file({
            "0": ["   XX   ", "  X  X  ", " X    X ", " X    X ",
                  " XXXXXX ", " X    X ", " X    X ", "        "]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_visual_format_mixed_zero_chars(self, grom_with_test_file):
        """Should parse visual format with mixed zero characters (0, _, ., space)"""
        grom = grom_with_test_file({
            "0": ["0_.XX. _", "..X0.X..", ".X....X0", " X.00.X.",
                  "0XXXXXX_", ".X.. .X_", " X.0  X0", "0_. 0_. "]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_visual_format_any_char_is_one(self, grom_with_test_file):
        """Should parse visual format where any non-zero char is 1"""
        grom = grom_with_test_file({
            "0": ["...AB...", "..C..D..", ".E....F.", ".G....H.",
                  ".IJKLMN.", ".O....P.", ".Q....R.", "........"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_parse_visual_format_with_symbols(self, grom_with_test_file):
        """Should parse visual format with symbols as 1"""
        grom = grom_with_test_file({
            "0": ["...##...", "..#..#..", ".#....#.", ".#....#.",
                  ".######.", ".#....#.", ".#....#.", "........"]
        })
        card = grom.get_card(0)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_visual_format_letter_zero(self, grom_with_test_file):
        """Should parse visual format for number '0' character"""
        # 0x18=00011000, 0x24=00100100, 0x42=01000010, 0x18=00011000
        grom = grom_with_test_file({
            "16": ["...XX...", "..X..X..", ".X....X.", ".X....X.",
                   ".X....X.", ".X....X.", "..X..X..", "...XX..."]
        })
        card = grom.get_card(16)
        assert card == [0x18, 0x24, 0x42, 0x42, 0x42, 0x42, 0x24, 0x18]

    def test_mixed_visual_and_numeric_formats(self, grom_with_test_file):
        """Should handle mixing visual format with numeric formats"""
        grom = grom_with_test_file({
            "0": ["...XX...", "..X..X..", 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00],
            "1": [0x18, 0x24, ".X....X.", ".X....X.", ".XXXXXX.", 0x42, 0x42, 0x00]
        })
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        assert grom.get_card(1) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_hex_card_key(self, grom_with_test_file):
        """Should accept hex card numbers with $ prefix"""
        grom = grom_with_test_file({
            "$00": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00],
            "$21": [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80]
        })
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        assert grom.get_card(0x21) == [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80]

    def test_hex_data_values(self, grom_with_test_file):
        """Should parse $ prefixed hex values in data"""
        grom = grom_with_test_file({
            "0": ["$18", "$24", "$42", "$42", "$7E", "$42", "$42", "$00"]
        })
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_hex_key_precedence(self, grom_with_test_file):
        """Hex card key should take precedence over decimal key"""
        grom = grom_with_test_file({
            "0": [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
            "$00": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        })
        # Hex key should win
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]

    def test_hex_key_with_label(self, grom_with_test_file):
        """Should support hex card keys with labels"""
        grom = grom_with_test_file({
            "$00": {
                "data": ["$18", "$24", "$42", "$42", "$7E", "$42", "$42", "$00"],
                "label": "Test Card"
            }
        })
        assert grom.get_card(0) == [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
        assert grom.get_label(0) == "Test Card"
