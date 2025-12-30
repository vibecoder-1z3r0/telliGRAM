# telliGRAM

A powerful Intellivision GRAM card creator for both **IntyBASIC** and **Intellivision Assembly** (as1600 / CP1610).

Convert your pixel art, sprite sheets, and ASCII art into ready-to-use GRAM card definitions for Intellivision game development.

## What are GRAM Cards?

GRAM (Graphics RAM) cards are user-definable 8×8 pixel graphics on the Intellivision. Unlike the built-in GROM (Graphics ROM) character set, GRAM allows you to create custom sprites, animations, and background tiles for your games.

- **64 cards total** (numbered 256-319)
- **8×8 pixels** per card
- **1-bit graphics** (2 colors per card)
- **~18 cards** can be loaded per frame

## Features

- 🎨 Convert images to GRAM card data
- 📝 Support for ASCII art input
- 🔄 Output to IntyBASIC or Assembly formats
- 📦 Batch processing for sprite sheets
- ✅ Automatic validation (dimensions, colors, limits)
- 🎯 Smart GROM detection (avoid wasting GRAM on built-in characters)

## Quick Start

```bash
# Convert an 8×8 PNG to IntyBASIC format
telligram sprite.png -o sprite.bas -f intybasic

# Convert sprite sheet to assembly (binary format)
telligram spritesheet.png -o sprites.asm -f assembly-bin

# ASCII art to assembly (hexadecimal format)
telligram ascii_art.txt -o graphics.asm -f assembly-hex
```

## Output Examples

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

# Install telliGRAM
pip install -e .
```

## Usage

### Basic Usage

```bash
# Convert image to IntyBASIC
telligram input.png -o output.bas -f intybasic

# Convert to assembly (binary format)
telligram input.png -o output.asm -f assembly-bin

# Convert to assembly (hexadecimal format)
telligram input.png -o output.asm -f assembly-hex
```

### Advanced Options

```bash
# Sprite sheet with custom label
telligram sheet.png -o sprites.bas -f intybasic -l game_sprites --grid 8x8

# Batch processing
telligram sprites/*.png -o output/ -f assembly-bin

# Interactive mode
telligram -i

# ASCII art input
telligram --ascii art.txt -o output.bas
```

### Configuration File

Create a `.telligram.yaml` file in your project:

```yaml
output_format: assembly-bin
label_prefix: gfx_
indentation: 8
comments: true
visual_preview: true

intybasic:
  pixel_on: 'X'
  pixel_off: '.'

assembly:
  format: binary  # or hexadecimal
  include_visual: true
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

🚧 **Currently in development** - See [PROJECT_REQUIREMENTS.md](docs/PROJECT_REQUIREMENTS.md) for roadmap

### Phase 1: Core Functionality (MVP)
- [ ] Card data structure
- [ ] ASCII art input parser
- [ ] IntyBASIC output formatter
- [ ] Assembly output formatter (binary)
- [ ] Basic CLI
- [ ] Unit tests

### Phase 2: Image Support
- [ ] Image file input (PNG)
- [ ] Color detection and validation
- [ ] Sprite sheet extraction
- [ ] Grid detection

### Phase 3: Advanced Features
- [ ] Assembly hexadecimal output
- [ ] Visual preview
- [ ] Configuration file support
- [ ] Batch processing

## Examples

Check the `examples/` folder for:
- Sample sprite PNG files
- ASCII art templates
- Expected output files (IntyBASIC and Assembly)
- Complete usage examples

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Credits

Created by **Vibe-Coder 1.z3r0**

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
