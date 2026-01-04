"""
Tests for GramCard class

Following TDD: Write tests FIRST, then implement to make them pass
"""
import pytest
from telligram.core.card import GramCard


class TestGramCardCreation:
    """Test basic GramCard creation and initialization"""

    def test_create_empty_card(self):
        """Should create 8×8 card with all pixels off"""
        card = GramCard()
        assert card.width == 8
        assert card.height == 8
        assert card.get_pixel(0, 0) == 0
        assert card.get_pixel(7, 7) == 0

    def test_create_card_with_data(self):
        """Should create card from 8 bytes of data"""
        data = [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF]
        card = GramCard(data)
        assert card.get_pixel(0, 0) == 1  # Top-left bit of 0xFF
        assert card.get_pixel(1, 1) == 0  # Second bit of 0x81

    def test_invalid_data_length_raises_error(self):
        """Should raise ValueError if data is not 8 bytes"""
        with pytest.raises(ValueError, match="8 bytes"):
            GramCard([0xFF, 0x81])  # Only 2 bytes

    def test_invalid_data_type_raises_error(self):
        """Should raise ValueError for invalid byte values"""
        with pytest.raises(ValueError, match="0-255"):
            GramCard([256, 0, 0, 0, 0, 0, 0, 0])  # 256 > 255


class TestGramCardPixelOperations:
    """Test pixel get/set operations"""

    def test_get_pixel(self):
        """Should get individual pixel value"""
        card = GramCard([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00])
        assert card.get_pixel(0, 0) == 1  # First row, all 1s
        assert card.get_pixel(0, 1) == 0  # Second row, all 0s
        assert card.get_pixel(7, 0) == 1  # Last pixel of first row

    def test_set_pixel(self):
        """Should set individual pixel"""
        card = GramCard()
        card.set_pixel(3, 4, 1)
        assert card.get_pixel(3, 4) == 1

    def test_clear_pixel(self):
        """Should clear individual pixel"""
        card = GramCard([0xFF] * 8)  # All pixels on
        card.set_pixel(3, 4, 0)
        assert card.get_pixel(3, 4) == 0

    def test_out_of_bounds_get_raises_error(self):
        """Should raise IndexError for invalid coordinates"""
        card = GramCard()
        with pytest.raises(IndexError):
            card.get_pixel(8, 0)
        with pytest.raises(IndexError):
            card.get_pixel(0, 8)
        with pytest.raises(IndexError):
            card.get_pixel(-1, 0)

    def test_out_of_bounds_set_raises_error(self):
        """Should raise IndexError when setting invalid coordinates"""
        card = GramCard()
        with pytest.raises(IndexError):
            card.set_pixel(8, 0, 1)
        with pytest.raises(IndexError):
            card.set_pixel(0, 8, 1)


class TestGramCardDataExport:
    """Test exporting card data in various formats"""

    def test_to_bytes(self):
        """Should export card as 8 bytes"""
        data = [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF]
        card = GramCard(data)
        assert card.to_bytes() == data

    def test_to_binary_strings(self):
        """Should export as binary string list"""
        card = GramCard([0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00])
        result = card.to_binary_strings()
        assert result[0] == "11111111"
        assert result[1] == "10000001"
        assert result[2] == "00000000"
        assert result[3] == "01000010"

    def test_to_hex_strings(self):
        """Should export as hex string list"""
        card = GramCard([0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00])
        result = card.to_hex_strings()
        assert result[0] == "FF"
        assert result[1] == "81"
        assert result[2] == "00"
        assert result[3] == "42"

    def test_to_dict(self):
        """Should export as dictionary for JSON serialization"""
        card = GramCard([0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00])
        card.label = "test_card"
        result = card.to_dict()
        assert result["label"] == "test_card"
        assert result["data"] == [0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00]

    def test_from_dict(self):
        """Should create card from dictionary"""
        data_dict = {
            "label": "test_card",
            "data": [0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00]
        }
        card = GramCard.from_dict(data_dict)
        assert card.label == "test_card"
        assert card.to_bytes() == [0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00]


class TestGramCardTransforms:
    """Test card transformation operations"""

    def test_flip_horizontal(self):
        """Should flip card horizontally"""
        # Create L-shape: 11110000
        card = GramCard([0xF0, 0x80, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00])
        card.flip_horizontal()
        # Should become: 00001111
        assert card.to_bytes()[0] == 0x0F
        assert card.to_bytes()[1] == 0x01

    def test_flip_vertical(self):
        """Should flip card vertically"""
        card = GramCard([0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        card.flip_vertical()
        result = card.to_bytes()
        assert result[0] == 0x00
        assert result[7] == 0xFF

    def test_clear(self):
        """Should clear all pixels"""
        card = GramCard([0xFF] * 8)
        card.clear()
        assert card.to_bytes() == [0x00] * 8

    def test_invert(self):
        """Should invert all pixels"""
        card = GramCard([0xFF, 0x00, 0xAA, 0x55, 0x00, 0x00, 0x00, 0x00])
        card.invert()
        result = card.to_bytes()
        assert result[0] == 0x00
        assert result[1] == 0xFF
        assert result[2] == 0x55
        assert result[3] == 0xAA


class TestGramCardProperties:
    """Test card properties and metadata"""

    def test_label_property(self):
        """Should have label property"""
        card = GramCard()
        card.label = "player_ship"
        assert card.label == "player_ship"

    def test_default_label(self):
        """Should have empty default label"""
        card = GramCard()
        assert card.label == ""

    def test_is_empty(self):
        """Should detect if card is empty"""
        card = GramCard()
        assert card.is_empty() is True

        card.set_pixel(0, 0, 1)
        assert card.is_empty() is False


class TestGramCardEdgeCases:
    """Test edge cases and special scenarios"""

    def test_all_pixels_on(self):
        """Should handle card with all pixels on"""
        card = GramCard([0xFF] * 8)
        for y in range(8):
            for x in range(8):
                assert card.get_pixel(x, y) == 1

    def test_all_pixels_off(self):
        """Should handle card with all pixels off"""
        card = GramCard([0x00] * 8)
        for y in range(8):
            for x in range(8):
                assert card.get_pixel(x, y) == 0

    def test_checkerboard_pattern(self):
        """Should correctly handle alternating pattern"""
        # Checkerboard: 0xAA = 10101010, 0x55 = 01010101
        card = GramCard([0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55])
        assert card.get_pixel(0, 0) == 1  # First bit of 0xAA
        assert card.get_pixel(1, 0) == 0
        assert card.get_pixel(0, 1) == 0  # First bit of 0x55
        assert card.get_pixel(1, 1) == 1
