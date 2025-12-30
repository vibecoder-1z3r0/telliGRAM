# telliGRAM - TDD Implementation Plan

## Development Philosophy

**Test-Driven Development (TDD) - Red-Green-Refactor Cycle**

1. 🔴 **RED** - Write a failing test
2. 🟢 **GREEN** - Write minimal code to make it pass
3. 🔵 **REFACTOR** - Improve code while keeping tests green

## Project Architecture

```
telliGRAM/
├── src/
│   └── telligram/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/                    # Core data models (Pure Python, 100% testable)
│       │   ├── __init__.py
│       │   ├── card.py              # GramCard class
│       │   ├── grom.py              # GromDatabase class
│       │   ├── animation.py         # Animation, Frame classes
│       │   ├── screen.py            # BacktabScreen class
│       │   └── project.py           # Project save/load
│       ├── codegen/                 # Code generators (Pure Python, 100% testable)
│       │   ├── __init__.py
│       │   ├── intybasic.py         # IntyBASIC generator
│       │   ├── assembly.py          # Assembly generator
│       │   └── screen_data.py       # BACKTAB data generator
│       ├── gui/                     # GUI layer (Light integration tests)
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── widgets/
│       │   │   ├── __init__.py
│       │   │   ├── pixel_editor.py  # 8×8 editor widget
│       │   │   ├── card_list.py     # GRAM card list
│       │   │   ├── animation_timeline.py
│       │   │   ├── screen_layout.py # 20×12 BACKTAB editor
│       │   │   └── grom_picker.py   # GROM character picker
│       │   └── dialogs/
│       │       ├── __init__.py
│       │       ├── export_dialog.py
│       │       └── preferences_dialog.py
│       └── utils/
│           ├── __init__.py
│           └── colors.py            # Intellivision color palette
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── core/
│   │   ├── test_card.py
│   │   ├── test_grom.py
│   │   ├── test_animation.py
│   │   ├── test_screen.py
│   │   └── test_project.py
│   ├── codegen/
│   │   ├── test_intybasic.py
│   │   ├── test_assembly.py
│   │   └── test_screen_data.py
│   ├── gui/                         # GUI integration tests
│   │   └── test_widgets.py
│   └── integration/
│       └── test_end_to_end.py
├── examples/
│   ├── sample_project.telligram
│   └── expected_output/
│       ├── player_walk.bas
│       └── player_walk.asm
├── requirements.txt
├── requirements-dev.txt             # Testing dependencies
├── setup.py
├── pytest.ini
└── .coverage
```

---

## Phase 1: Core Data Models (TDD Foundation)

### Iteration 1.1: GramCard Class

#### 🔴 RED - Write Tests First

**File:** `tests/core/test_card.py`

```python
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
        assert card.get_pixel(1, 0) == 0  # Second pixel of 0x81

    def test_invalid_data_raises_error(self):
        """Should raise ValueError if data is not 8 bytes"""
        with pytest.raises(ValueError):
            GramCard([0xFF, 0x81])  # Only 2 bytes

class TestGramCardPixelOperations:
    """Test pixel get/set operations"""

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

    def test_out_of_bounds_raises_error(self):
        """Should raise IndexError for invalid coordinates"""
        card = GramCard()
        with pytest.raises(IndexError):
            card.get_pixel(8, 0)
        with pytest.raises(IndexError):
            card.set_pixel(0, 8, 1)

class TestGramCardDataExport:
    """Test exporting card data"""

    def test_to_bytes(self):
        """Should export card as 8 bytes"""
        data = [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF]
        card = GramCard(data)
        assert card.to_bytes() == data

    def test_to_binary_strings(self):
        """Should export as binary string list"""
        card = GramCard([0xFF, 0x81, 0x00, 0x42])
        result = card.to_binary_strings()
        assert result[0] == "11111111"
        assert result[1] == "10000001"
        assert result[2] == "00000000"
        assert result[3] == "01000010"

    def test_to_hex_strings(self):
        """Should export as hex string list"""
        card = GramCard([0xFF, 0x81, 0x00, 0x42])
        result = card.to_hex_strings()
        assert result[0] == "FF"
        assert result[1] == "81"
        assert result[2] == "00"
        assert result[3] == "42"
```

#### 🟢 GREEN - Implement Minimal Code

**File:** `src/telligram/core/card.py`

```python
"""GRAM Card data model"""
from typing import List, Optional

class GramCard:
    """Represents a single 8×8 GRAM card"""

    WIDTH = 8
    HEIGHT = 8

    def __init__(self, data: Optional[List[int]] = None):
        """
        Initialize GRAM card

        Args:
            data: Optional list of 8 bytes (one per row)

        Raises:
            ValueError: If data is not 8 bytes
        """
        if data is None:
            self._data = [0] * self.HEIGHT
        else:
            if len(data) != self.HEIGHT:
                raise ValueError(f"Card data must be {self.HEIGHT} bytes")
            self._data = list(data)

    @property
    def width(self) -> int:
        return self.WIDTH

    @property
    def height(self) -> int:
        return self.HEIGHT

    def get_pixel(self, x: int, y: int) -> int:
        """
        Get pixel value at (x, y)

        Args:
            x: Column (0-7)
            y: Row (0-7)

        Returns:
            0 or 1

        Raises:
            IndexError: If coordinates out of bounds
        """
        if not (0 <= x < self.WIDTH and 0 <= y < self.HEIGHT):
            raise IndexError(f"Pixel coordinates ({x}, {y}) out of bounds")

        byte = self._data[y]
        bit = 7 - x  # MSB is leftmost pixel
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
            raise IndexError(f"Pixel coordinates ({x}, {y}) out of bounds")

        bit = 7 - x
        if value:
            self._data[y] |= (1 << bit)  # Set bit
        else:
            self._data[y] &= ~(1 << bit)  # Clear bit

    def to_bytes(self) -> List[int]:
        """Export card as list of 8 bytes"""
        return list(self._data)

    def to_binary_strings(self) -> List[str]:
        """Export as list of binary strings"""
        return [format(byte, '08b') for byte in self._data]

    def to_hex_strings(self) -> List[str]:
        """Export as list of hex strings"""
        return [format(byte, '02X') for byte in self._data]
```

#### 🔵 REFACTOR - Improve Code

**File:** `tests/core/test_card.py` (Add more edge cases)

```python
class TestGramCardEdgeCases:
    """Test edge cases and special scenarios"""

    def test_all_pixels_on(self):
        """Should handle card with all pixels on"""
        card = GramCard([0xFF] * 8)
        for y in range(8):
            for x in range(8):
                assert card.get_pixel(x, y) == 1

    def test_checkerboard_pattern(self):
        """Should correctly handle alternating pattern"""
        # Checkerboard: 0xAA = 10101010
        card = GramCard([0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55])
        assert card.get_pixel(0, 0) == 1  # First bit of 0xAA
        assert card.get_pixel(1, 0) == 0
        assert card.get_pixel(0, 1) == 0  # First bit of 0x55
        assert card.get_pixel(1, 1) == 1
```

---

### Iteration 1.2: GROM Database Class

#### 🔴 RED - Write Tests First

**File:** `tests/core/test_grom.py`

```python
import pytest
from telligram.core.grom import GromDatabase, GromCard

class TestGromDatabase:
    """Test GROM character database"""

    def test_get_card_by_number(self):
        """Should retrieve GROM card by number (0-255)"""
        db = GromDatabase()
        card = db.get_card(33)  # Letter 'A'
        assert card is not None
        assert card.number == 33

    def test_get_card_by_ascii(self):
        """Should retrieve card by ASCII character"""
        db = GromDatabase()
        card = db.get_card_for_char('A')
        assert card.number == 33  # 'A' = ASCII 65, GROM 33

    def test_ascii_to_grom_conversion(self):
        """Should convert ASCII code to GROM card number"""
        db = GromDatabase()
        assert db.ascii_to_grom(65) == 33   # 'A'
        assert db.ascii_to_grom(48) == 16   # '0'
        assert db.ascii_to_grom(32) == 0    # space

    def test_grom_to_ascii_conversion(self):
        """Should convert GROM card to ASCII code"""
        db = GromDatabase()
        assert db.grom_to_ascii(33) == 65   # 'A'
        assert db.grom_to_ascii(16) == 48   # '0'
        assert db.grom_to_ascii(0) == 32    # space

    def test_invalid_grom_number(self):
        """Should raise ValueError for invalid GROM number"""
        db = GromDatabase()
        with pytest.raises(ValueError):
            db.get_card(256)  # Out of range

    def test_string_to_grom_cards(self):
        """Should convert string to list of GROM card numbers"""
        db = GromDatabase()
        result = db.string_to_cards("HELLO")
        assert result == [40, 37, 44, 44, 47]  # H E L L O

class TestGromCardInfo:
    """Test GROM card information"""

    def test_card_has_description(self):
        """GROM cards should have text description"""
        db = GromDatabase()
        card = db.get_card(33)
        assert card.description == 'A'
        assert card.category == 'letter'

    def test_card_has_ascii_range(self):
        """Should identify which cards are ASCII"""
        db = GromDatabase()
        assert db.is_ascii_card(33) is True   # 'A'
        assert db.is_ascii_card(128) is False  # Extended
```

#### 🟢 GREEN - Implement

**File:** `src/telligram/core/grom.py`

```python
"""GROM character database"""
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class GromCard:
    """Information about a GROM character"""
    number: int
    description: str
    category: str
    ascii_code: Optional[int] = None

class GromDatabase:
    """Database of GROM characters (0-255)"""

    # ASCII mapping: GROM 0-94 = ASCII 32-126
    ASCII_OFFSET = 32
    ASCII_GROM_MAX = 94

    def __init__(self):
        """Initialize GROM database"""
        self._cards = self._build_database()

    def _build_database(self) -> dict:
        """Build GROM card database"""
        cards = {}

        # ASCII characters (0-94)
        for grom_num in range(self.ASCII_GROM_MAX + 1):
            ascii_code = grom_num + self.ASCII_OFFSET
            char = chr(ascii_code)

            # Categorize
            if char.isalpha():
                category = 'letter'
            elif char.isdigit():
                category = 'number'
            elif char.isspace():
                category = 'space'
            else:
                category = 'symbol'

            cards[grom_num] = GromCard(
                number=grom_num,
                description=char,
                category=category,
                ascii_code=ascii_code
            )

        # Extended characters (95-255)
        # TODO: Add specific GROM extended characters
        for grom_num in range(95, 256):
            cards[grom_num] = GromCard(
                number=grom_num,
                description=f'Extended {grom_num}',
                category='extended',
                ascii_code=None
            )

        return cards

    def get_card(self, number: int) -> GromCard:
        """Get GROM card by number (0-255)"""
        if not (0 <= number <= 255):
            raise ValueError(f"GROM card number must be 0-255, got {number}")
        return self._cards[number]

    def get_card_for_char(self, char: str) -> Optional[GromCard]:
        """Get GROM card for ASCII character"""
        if len(char) != 1:
            raise ValueError("char must be single character")

        ascii_code = ord(char)
        grom_num = self.ascii_to_grom(ascii_code)

        if grom_num is not None:
            return self.get_card(grom_num)
        return None

    def ascii_to_grom(self, ascii_code: int) -> Optional[int]:
        """Convert ASCII code to GROM card number"""
        if 32 <= ascii_code <= 126:
            return ascii_code - self.ASCII_OFFSET
        return None

    def grom_to_ascii(self, grom_num: int) -> Optional[int]:
        """Convert GROM card number to ASCII code"""
        if 0 <= grom_num <= self.ASCII_GROM_MAX:
            return grom_num + self.ASCII_OFFSET
        return None

    def is_ascii_card(self, grom_num: int) -> bool:
        """Check if GROM card is ASCII character"""
        return 0 <= grom_num <= self.ASCII_GROM_MAX

    def string_to_cards(self, text: str) -> List[int]:
        """Convert string to list of GROM card numbers"""
        result = []
        for char in text:
            card_num = self.ascii_to_grom(ord(char))
            if card_num is not None:
                result.append(card_num)
        return result
```

---

### Iteration 1.3: Animation Classes

#### 🔴 RED - Write Tests First

**File:** `tests/core/test_animation.py`

```python
import pytest
from telligram.core.animation import Animation, Frame

class TestFrame:
    """Test animation Frame class"""

    def test_create_frame(self):
        """Should create frame with card ID and duration"""
        frame = Frame(card_id=256, duration=4)
        assert frame.card_id == 256
        assert frame.duration == 4
        assert frame.flip_h is False
        assert frame.flip_v is False

    def test_frame_with_flips(self):
        """Should support horizontal/vertical flips"""
        frame = Frame(card_id=256, duration=4, flip_h=True, flip_v=True)
        assert frame.flip_h is True
        assert frame.flip_v is True

    def test_invalid_duration(self):
        """Should raise ValueError for invalid duration"""
        with pytest.raises(ValueError):
            Frame(card_id=256, duration=0)
        with pytest.raises(ValueError):
            Frame(card_id=256, duration=-1)

class TestAnimation:
    """Test Animation class"""

    def test_create_empty_animation(self):
        """Should create empty animation"""
        anim = Animation(name="test")
        assert anim.name == "test"
        assert len(anim.frames) == 0
        assert anim.loop is True

    def test_add_frame(self):
        """Should add frames to animation"""
        anim = Animation(name="walk")
        anim.add_frame(Frame(card_id=256, duration=4))
        anim.add_frame(Frame(card_id=257, duration=4))
        assert len(anim.frames) == 2

    def test_remove_frame(self):
        """Should remove frame by index"""
        anim = Animation(name="walk")
        anim.add_frame(Frame(card_id=256, duration=4))
        anim.add_frame(Frame(card_id=257, duration=4))
        anim.remove_frame(0)
        assert len(anim.frames) == 1
        assert anim.frames[0].card_id == 257

    def test_total_duration(self):
        """Should calculate total duration in ticks"""
        anim = Animation(name="walk")
        anim.add_frame(Frame(card_id=256, duration=4))
        anim.add_frame(Frame(card_id=257, duration=6))
        anim.add_frame(Frame(card_id=258, duration=8))
        assert anim.total_duration == 18

    def test_total_duration_seconds(self):
        """Should calculate duration in seconds @ 60Hz"""
        anim = Animation(name="walk")
        anim.add_frame(Frame(card_id=256, duration=60))
        assert anim.total_duration_seconds(60) == 1.0
        assert anim.total_duration_seconds(50) == 1.2

    def test_get_frame_at_tick(self):
        """Should get frame at specific tick"""
        anim = Animation(name="walk", loop=True)
        anim.add_frame(Frame(card_id=256, duration=10))
        anim.add_frame(Frame(card_id=257, duration=10))
        anim.add_frame(Frame(card_id=258, duration=10))

        assert anim.get_frame_at_tick(0).card_id == 256
        assert anim.get_frame_at_tick(5).card_id == 256
        assert anim.get_frame_at_tick(10).card_id == 257
        assert anim.get_frame_at_tick(25).card_id == 258

    def test_loop_wraps_around(self):
        """Should wrap around when loop=True"""
        anim = Animation(name="walk", loop=True)
        anim.add_frame(Frame(card_id=256, duration=10))
        anim.add_frame(Frame(card_id=257, duration=10))

        assert anim.get_frame_at_tick(30).card_id == 256  # Wraps

    def test_no_loop_stops_at_end(self):
        """Should stop at last frame when loop=False"""
        anim = Animation(name="explode", loop=False)
        anim.add_frame(Frame(card_id=256, duration=10))
        anim.add_frame(Frame(card_id=257, duration=10))

        assert anim.get_frame_at_tick(30).card_id == 257  # Stays on last
```

#### 🟢 GREEN - Implement

**File:** `src/telligram/core/animation.py`

```python
"""Animation system for GRAM cards"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Frame:
    """Single animation frame"""
    card_id: int          # GRAM card ID (256-319)
    duration: int         # Duration in ticks (1 tick = 1/60 sec @ 60Hz)
    flip_h: bool = False  # Horizontal flip
    flip_v: bool = False  # Vertical flip

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError("Frame duration must be positive")

@dataclass
class Animation:
    """Animation sequence"""
    name: str
    frames: List[Frame] = field(default_factory=list)
    loop: bool = True
    ping_pong: bool = False

    def add_frame(self, frame: Frame) -> None:
        """Add frame to animation"""
        self.frames.append(frame)

    def remove_frame(self, index: int) -> None:
        """Remove frame by index"""
        del self.frames[index]

    @property
    def total_duration(self) -> int:
        """Total duration in ticks"""
        return sum(frame.duration for frame in self.frames)

    def total_duration_seconds(self, fps: int = 60) -> float:
        """Total duration in seconds"""
        return self.total_duration / fps

    def get_frame_at_tick(self, tick: int) -> Optional[Frame]:
        """Get frame at specific tick"""
        if not self.frames:
            return None

        total = self.total_duration

        # Handle looping
        if self.loop and tick >= total:
            tick = tick % total
        elif tick >= total:
            return self.frames[-1]  # Stay on last frame

        # Find frame at tick
        elapsed = 0
        for frame in self.frames:
            if tick < elapsed + frame.duration:
                return frame
            elapsed += frame.duration

        return self.frames[-1]
```

---

## Phase 2: Code Generators (TDD)

### Iteration 2.1: IntyBASIC Generator

#### 🔴 RED - Write Tests First

**File:** `tests/codegen/test_intybasic.py`

```python
import pytest
from telligram.core.card import GramCard
from telligram.core.animation import Animation, Frame
from telligram.codegen.intybasic import IntyBasicGenerator

class TestIntyBasicCardGeneration:
    """Test generating IntyBASIC BITMAP statements"""

    def test_generate_single_card(self):
        """Should generate BITMAP statements for one card"""
        card = GramCard([0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF])
        gen = IntyBasicGenerator()
        result = gen.generate_card(card, label="test_card")

        expected = '''test_card:
    BITMAP "XXXXXXXX"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "XXXXXXXX"'''

        assert result.strip() == expected.strip()

    def test_custom_pixel_characters(self):
        """Should support custom pixel on/off characters"""
        card = GramCard([0xC0, 0x00])  # 11000000, 00000000
        gen = IntyBasicGenerator(pixel_on='#', pixel_off='.')
        result = gen.generate_card(card, label="test")

        assert '    BITMAP "##......"' in result
        assert '    BITMAP "........"' in result

    def test_generate_multiple_cards(self):
        """Should generate multiple consecutive cards"""
        cards = [
            GramCard([0xFF] * 8),
            GramCard([0x00] * 8),
        ]
        gen = IntyBasicGenerator()
        result = gen.generate_cards(cards, label="sprites")

        assert "sprites:" in result
        assert result.count("BITMAP") == 16  # 8 per card × 2

    def test_generate_with_define_statement(self):
        """Should optionally include DEFINE statement"""
        card = GramCard([0xFF] * 8)
        gen = IntyBasicGenerator()
        result = gen.generate_card(
            card,
            label="test",
            include_define=True,
            gram_slot=0
        )

        assert "DEFINE 0, 1, test" in result
        assert "WAIT" in result

class TestIntyBasicAnimationGeneration:
    """Test generating animation data"""

    def test_generate_animation_arrays(self):
        """Should generate frame and timing DATA arrays"""
        anim = Animation(name="walk")
        anim.add_frame(Frame(card_id=256, duration=4))
        anim.add_frame(Frame(card_id=257, duration=4))
        anim.add_frame(Frame(card_id=258, duration=6))

        gen = IntyBasicGenerator()
        result = gen.generate_animation(anim)

        assert "walk_frames:" in result
        assert "DATA 256, 257, 258" in result
        assert "walk_timing:" in result
        assert "DATA 4, 4, 6" in result

    def test_generate_animation_playback_code(self):
        """Should generate animation playback helper code"""
        anim = Animation(name="walk")
        anim.add_frame(Frame(card_id=256, duration=4))

        gen = IntyBasicGenerator()
        result = gen.generate_animation(anim, include_playback=True)

        assert "anim_frame" in result
        assert "anim_timer" in result
```

#### 🟢 GREEN - Implement

**File:** `src/telligram/codegen/intybasic.py`

```python
"""IntyBASIC code generator"""
from typing import List, Optional
from telligram.core.card import GramCard
from telligram.core.animation import Animation

class IntyBasicGenerator:
    """Generate IntyBASIC code for GRAM cards and animations"""

    def __init__(self, pixel_on: str = 'X', pixel_off: str = '.'):
        self.pixel_on = pixel_on
        self.pixel_off = pixel_off

    def generate_card(
        self,
        card: GramCard,
        label: str,
        include_define: bool = False,
        gram_slot: Optional[int] = None
    ) -> str:
        """Generate BITMAP statements for a single card"""
        lines = [f"{label}:"]

        # Generate BITMAP statements
        for y in range(card.height):
            row = ""
            for x in range(card.width):
                pixel = card.get_pixel(x, y)
                row += self.pixel_on if pixel else self.pixel_off
            lines.append(f'    BITMAP "{row}"')

        # Optional DEFINE statement
        if include_define and gram_slot is not None:
            lines.append("")
            lines.append(f"DEFINE {gram_slot}, 1, {label}")
            lines.append("WAIT")

        return "\n".join(lines)

    def generate_cards(self, cards: List[GramCard], label: str) -> str:
        """Generate multiple consecutive cards"""
        lines = [f"{label}:"]

        for i, card in enumerate(cards):
            if i > 0:
                lines.append("")
                lines.append(f"    ' Card {i}")

            for y in range(card.height):
                row = ""
                for x in range(card.width):
                    pixel = card.get_pixel(x, y)
                    row += self.pixel_on if pixel else self.pixel_off
                lines.append(f'    BITMAP "{row}"')

        return "\n".join(lines)

    def generate_animation(
        self,
        animation: Animation,
        include_playback: bool = False
    ) -> str:
        """Generate animation data arrays"""
        lines = []

        # Frame data
        lines.append(f"REM Animation: {animation.name}")
        lines.append(f"{animation.name}_frames:")
        frame_ids = [str(frame.card_id) for frame in animation.frames]
        lines.append(f"    DATA {', '.join(frame_ids)}")

        # Timing data
        lines.append(f"{animation.name}_timing:")
        durations = [str(frame.duration) for frame in animation.frames]
        lines.append(f"    DATA {', '.join(durations)}")

        # Optional playback code
        if include_playback:
            lines.append("")
            lines.append("REM Animation playback variables")
            lines.append("anim_frame = 0")
            lines.append("anim_timer = 0")

        return "\n".join(lines)
```

---

## Phase 3: GUI Foundation (Integration Tests)

### Iteration 3.1: Pixel Editor Widget

#### 🔴 RED - Write Tests First

**File:** `tests/gui/test_pixel_editor.py`

```python
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from telligram.gui.widgets.pixel_editor import PixelEditorWidget
from telligram.core.card import GramCard

@pytest.fixture
def qapp():
    """Create QApplication for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

class TestPixelEditorWidget:
    """Test pixel editor widget"""

    def test_create_widget(self, qapp):
        """Should create 8×8 pixel editor"""
        widget = PixelEditorWidget()
        assert widget.grid_size == 8

    def test_set_card(self, qapp):
        """Should display card data"""
        widget = PixelEditorWidget()
        card = GramCard([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00])
        widget.set_card(card)

        # Verify widget updated
        assert widget.card == card

    def test_mouse_click_toggles_pixel(self, qapp):
        """Should toggle pixel on mouse click"""
        widget = PixelEditorWidget()
        card = GramCard()
        widget.set_card(card)

        # Simulate click at pixel (3, 3)
        # Note: Actual position depends on widget size
        # This is a simplified test
        initial = card.get_pixel(3, 3)
        widget.toggle_pixel(3, 3)
        assert card.get_pixel(3, 3) == (1 - initial)

    def test_emits_changed_signal(self, qapp):
        """Should emit signal when card changes"""
        widget = PixelEditorWidget()
        card = GramCard()
        widget.set_card(card)

        changed = False
        def on_changed():
            nonlocal changed
            changed = True

        widget.card_changed.connect(on_changed)
        widget.toggle_pixel(0, 0)

        assert changed is True
```

---

## Development Workflow

### Test-First Development Process

For each feature:

1. **Write failing test** (`pytest -v`)
   ```bash
   pytest tests/core/test_card.py::TestGramCardCreation::test_create_empty_card -v
   # FAILED ❌
   ```

2. **Write minimal implementation**
   ```bash
   # Edit src/telligram/core/card.py
   pytest tests/core/test_card.py::TestGramCardCreation::test_create_empty_card -v
   # PASSED ✅
   ```

3. **Refactor and add edge cases**
   ```bash
   # Add more tests
   pytest tests/core/test_card.py -v
   # All PASSED ✅
   ```

4. **Check coverage**
   ```bash
   pytest --cov=src/telligram --cov-report=html
   # Aim for >90% coverage on core modules
   ```

### CI/CD Pipeline

**.github/workflows/test.yml**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Testing Configuration

**pytest.ini**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src/telligram
    --cov-report=term-missing
    --cov-report=html
markers =
    unit: Unit tests for core logic
    integration: Integration tests for GUI
    slow: Slow-running tests
```

**requirements-dev.txt**
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-qt>=4.2.0
PySide6>=6.5.0
```

---

## Coverage Goals

| Module | Target Coverage | Priority |
|--------|----------------|----------|
| `core/card.py` | 100% | Critical |
| `core/grom.py` | 100% | Critical |
| `core/animation.py` | 100% | Critical |
| `codegen/*.py` | 95%+ | High |
| `gui/widgets/*.py` | 70%+ | Medium |

---

## Next Steps

See **DEVELOPMENT_PHASES.md** for detailed iteration breakdown.
