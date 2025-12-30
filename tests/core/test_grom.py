"""
Tests for GROM (Graphics ROM) data module.

GROM contains 256 built-in characters (0-255) that are always available.
Cards 0-94 map to ASCII 32-126.
"""

import pytest
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
