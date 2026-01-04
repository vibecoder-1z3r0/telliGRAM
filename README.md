# telliGRAM

A cross platform visual editor built in Python and PySide for creating Intellivision GRAM cards, animations, and complete screen layouts (BACKTAB + MOBs) with support for **IntyBASIC** and **Intellivision Assembly** (as1600 / CP1610).

Create custom 8×8 graphics, animated sequences, and full screen designs for Intellivision games using an intuitive GUI with real-time editing and project management.

This project is not affiliated or endorsed by Atari Interactive, Inc.

## What are GRAM Cards?

GRAM (Graphics RAM) cards are user-definable 8×8 pixel graphics on the Intellivision. Unlike the built-in GROM (Graphics ROM) character set, GRAM allows you to create custom sprites, animations, and background tiles for your games.

- **64 cards total** (numbered 256-319)
- **8×8 pixels** per card
- **1-bit graphics** (2 colors per card)
- **~18 cards** can be loaded per frame

## Features

- 🎨 **Visual Pixel Editor** - Interactive 8×8 grid with click-and-drag painting
- 📦 **64-Card Project Manager** - Organize all GRAM cards in one project
- 💾 **Save/Load Projects** - JSON-based `.tlgm` file format
- 🔄 **Card Transformations** - Flip horizontal/vertical, clear, invert
- 👁️ **Live Preview** - See all 64 cards at once with thumbnail grid
- 📚 **GROM Browser** - Reference all 256 built-in Intellivision characters
- 🎬 **Animation Timeline** - Sequence GRAM cards with frame timing and playback
- 🖼️ **STIC Figures** - Complete screen layout designer with 20×12 BACKTAB grid and 8 MOBs
- ⌨️ **Keyboard Shortcuts** - Ctrl+N/O/S for quick file operations
- ✅ **Test-Driven Development** - 100% test coverage on core modules (71/71 tests passing)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI application
python3 -m telligram.main
```

## Planned Output Formats

Code generation is planned for future releases. The application will export to:

### IntyBASIC Format
```basic
player_ship:
    BITMAP "..XXXX.."
    BITMAP ".XXXXXX."
    BITMAP "XXXXXXXX"
    BITMAP "XX.XX.XX"
    BITMAP "X..XX..X"
    BITMAP "....XX.."
    BITMAP "...X..X."
    BITMAP "...X..X."
```

### Assembly Format (Binary)
```asm
player_ship:
        DECLE   %00111100    ; Row 0
        DECLE   %01111110    ; Row 1
        DECLE   %11111111    ; Row 2
        DECLE   %11011011    ; Row 3
        DECLE   %10011001    ; Row 4
        DECLE   %00011000    ; Row 5
        DECLE   %00100100    ; Row 6
        DECLE   %00100100    ; Row 7
```

### Assembly Format (Hexadecimal)
```asm
player_ship:
        DECLE   $3C    ; Row 0: ..XXXX..
        DECLE   $7E    ; Row 1: .XXXXXX.
        DECLE   $FF    ; Row 2: XXXXXXXX
        DECLE   $DB    ; Row 3: XX.XX.XX
        DECLE   $99    ; Row 4: X..XX..X
        DECLE   $18    ; Row 5: ....XX..
        DECLE   $24    ; Row 6: ...X..X.
        DECLE   $24    ; Row 7: ...X..X.
```

## Documentation

📚 **Comprehensive documentation available in the `docs/` folder:**

- **[GRAM Cards Overview](docs/GRAM_CARDS.md)** - Technical details about GRAM cards
- **[GROM Layout](docs/GROM_LAYOUT.md)** - Built-in character set reference (cards 0-255)
- **[IntyBASIC Format](docs/INTYBASIC_FORMAT.md)** - IntyBASIC BITMAP format specification
- **[Assembly Format](docs/ASSEMBLY_FORMAT.md)** - as1600 Assembly DECLE format specification
- **[Hardware Reference](docs/HARDWARE_REFERENCE.md)** - Complete Intellivision hardware quick reference
- **[Project Requirements](docs/PROJECT_REQUIREMENTS.md)** - Development roadmap and specifications

## Installation

```bash
# Clone the repository
git clone https://github.com/vibecoder-1z3r0/telliGRAM.git
cd telliGRAM

# Install dependencies
pip install -r requirements.txt
```

## Usage

### GUI Application

```bash
# Run the application
python3 -m telligram.main
```

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run with coverage report
python3 -m pytest tests/ --cov=telligram --cov-report=html

# Current status: 71/71 tests passing (100% core coverage)
```

## Technical Specifications

### GRAM Card Structure
- **Dimensions:** 8×8 pixels (64 pixels total)
- **Storage:** 8 bytes (1 byte per row)
- **Format:** 1-bit per pixel (binary: on/off)
- **Colors:** Defined separately (2 colors max per card)

### Memory Layout
- **GRAM Location:** `$3000-$33FF` (512 bytes)
- **Card Range:** 256-319 (64 cards)
- **Per-Frame Limit:** ~18 cards (NTSC)

### GROM vs GRAM
- **GROM (0-255):** Built-in ROM characters (text, symbols)
- **GRAM (256-319):** User-defined graphics (sprites, animations)

**Pro Tip:** Use GROM for text and common symbols, save GRAM for custom game graphics!

## Development Status

✅ **Phase 1: Core Data Models (COMPLETE)**
- [x] GramCard class with pixel manipulation
- [x] Project class with 64-card management
- [x] JSON save/load functionality (.telligram format)
- [x] Card transformations (flip H/V, invert, clear)
- [x] Comprehensive test suite (24 tests, 100% coverage)

✅ **Phase 2: Basic GUI (COMPLETE)**
- [x] Main application window with PySide6
- [x] 64-card grid view with thumbnails
- [x] Interactive 8×8 pixel editor
- [x] Real-time preview and updates
- [x] File menu (New, Open, Save, Save As)
- [x] Edit menu (Clear, Flip H/V)
- [x] Keyboard shortcuts

✅ **Phase 3: GROM & Animation (COMPLETE)**
- [x] GROM data model with all 256 built-in characters (14 tests)
- [x] GROM character browser widget (read-only reference)
- [x] Animation class for sequencing GRAM cards (18 tests)
- [x] Timeline editor with playback controls
- [x] Tabbed interface for GROM browser and timeline editor
- [x] Full project integration with save/load

✅ **Phase 4: STIC Figures - Screen Layout Designer (COMPLETE)**
- [x] 20×12 BACKTAB grid editor with visual canvas
- [x] Dual display modes: Color Stack and Foreground/Background
- [x] Real-time canvas rendering (48px tiles at 6× scale)
- [x] 8 MOBs (Moving Object Blocks) with full configuration
- [x] MOB properties: Position (X/Y), Card, Color, Priority, Size, Flip (H/V)
- [x] Card palette with GRAM/GROM tabs (conditional GROM display)
- [x] Figure management: Multiple figures per project with New/Rename/Delete/Import/Export
- [x] Project integration: Figures saved with .tlgm files

🚧 **Phase 5: Code Generation & Advanced Features (PLANNED)**
- [ ] IntyBASIC code export (BITMAP format)
- [ ] Assembly code export (DECLE format)
- [ ] BACKTAB/MOB export to IntyBASIC/Assembly
- [ ] Import from sprite sheets/images
- [ ] Undo/redo system for STIC Figures
- [ ] MOB animation support (link to Animation objects)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[MIT License](LICENSE)
[VCL-0.1-Experimental](https://github.com/tyraziel/vibe-coder-license)

## Credits

Created by **Vibe-Coder 1.z3r0**
[AIA PAI Nc Hin R Claude Code [Sonnet 4.5] v1.0](https://aiattribution.github.io/statements/AIA-PAI-Nc-Hin-R-?model=Claude%20Code%20%5BSonnet%204.5%5D-v1.0)

### References
- [Intellivision Wiki](https://wiki.intellivision.us/)
- [IntyBASIC by nanochess](https://nanochess.org/intybasic.html)
- [jzIntv SDK](http://spatula-city.org/~im14u2c/intv/)
- [as1600 Assembler Documentation](http://spatula-city.org/~im14u2c/intv/)

## Support

- 🐛 **Report bugs:** [GitHub Issues](https://github.com/vibecoder-1z3r0/telliGRAM/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/vibecoder-1z3r0/telliGRAM/discussions)
- 📖 **Documentation:** See `docs/` folder

---

**Happy GRAM card creation!** 🎮✨
