# telliGRAM - Project Requirements

## Project Overview

**telliGRAM** is a command-line tool for creating Intellivision GRAM cards from various input formats and exporting them as IntyBASIC or Intellivision Assembly code.

## Core Requirements

### Input Formats

The tool should accept multiple input formats:

1. **Image Files**
   - PNG, GIF, BMP formats
   - Automatically detect 8×8 regions
   - Support for sprite sheets (multiple 8×8 cards in one image)
   - Color detection (warn if >2 colors per card)
   - Dithering options for multi-color images

2. **Text ASCII Art**
   - Simple text-based pixel art
   - Multiple character conventions (X/., #/., 1/0, @/space)
   - Line-by-line input (8 lines per card)

3. **Binary Data**
   - Raw 8-byte binary format
   - Hexadecimal strings

4. **JSON/YAML**
   - Structured data format for batch processing
   - Metadata support (labels, descriptions, animation frames)

### Output Formats

#### IntyBASIC Output
```basic
label_name:
    BITMAP "XXXXXXXX"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "X......X"
    BITMAP "XXXXXXXX"
```

**Options:**
- Custom label names
- Configurable pixel characters (X/., #/., etc.)
- Batch output (multiple cards)
- Include DEFINE statements

#### Assembly Output (Binary Format)
```asm
label_name:
        DECLE   %11111111    ; Row 0
        DECLE   %10000001    ; Row 1
        DECLE   %10000001    ; Row 2
        DECLE   %10000001    ; Row 3
        DECLE   %10000001    ; Row 4
        DECLE   %10000001    ; Row 5
        DECLE   %10000001    ; Row 6
        DECLE   %11111111    ; Row 7
```

#### Assembly Output (Hexadecimal Format)
```asm
label_name:
        DECLE   $FF    ; Row 0: XXXXXXXX
        DECLE   $81    ; Row 1: X......X
        DECLE   $81    ; Row 2: X......X
        DECLE   $81    ; Row 3: X......X
        DECLE   $81    ; Row 4: X......X
        DECLE   $81    ; Row 5: X......X
        DECLE   $81    ; Row 6: X......X
        DECLE   $FF    ; Row 7: XXXXXXXX
```

**Options:**
- Binary (`%`) or hexadecimal (`$`) format
- Visual comments (ASCII art representation)
- Block comments with full card preview
- Custom indentation
- Include copy-to-GRAM code

### Validation

The tool must validate:

1. **Card Dimensions**
   - Exactly 8×8 pixels per card
   - Warn if dimensions don't match

2. **Color Constraints**
   - Maximum 2 colors per card
   - Warn/error on violation
   - Suggest color reduction

3. **GRAM Limits**
   - Maximum 64 cards total
   - Warn if exceeding capacity

4. **Format Compliance**
   - Valid binary/hex values (0-255)
   - Proper string lengths

### Features

#### Essential Features
- Convert images to GRAM card data
- Output IntyBASIC BITMAP format
- Output Assembly DECLE format (binary)
- Output Assembly DECLE format (hexadecimal)
- Support single and multiple cards
- Custom label naming
- Basic error checking

#### Advanced Features
- Sprite sheet extraction (auto-detect 8×8 grid)
- Animation frame sequences
- Color palette optimization
- Preview output (visual representation)
- Batch processing (multiple files)
- Interactive mode (CLI wizard)
- Configuration file support
- Template system for output formatting

#### Nice-to-Have Features
- GUI preview window
- Live editing/preview
- Import from existing GRAM data
- Reverse conversion (code → image)
- Integration with graphics editors
- Animation preview
- Optimization suggestions
- GROM character detection (warn when duplicating GROM)

## Technical Specifications

### Command-Line Interface

```bash
# Basic usage
telligram input.png -o output.asm -f assembly-bin

# Multiple cards from sprite sheet
telligram spritesheet.png -o sprites.bas -f intybasic --grid 8x8

# Custom label
telligram player.png -o player.asm -f assembly-hex -l player_sprite

# Batch processing
telligram *.png -o graphics/ -f intybasic

# Interactive mode
telligram -i

# ASCII art input
telligram --ascii -o output.bas << EOF
XXXXXXXX
X......X
X......X
X......X
X......X
X......X
X......X
XXXXXXXX
EOF
```

### Configuration File

Support for `.telligram.yaml` or `.telligram.json`:

```yaml
# .telligram.yaml
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
  indentation: 8
```

### Project Structure

```
telliGRAM/
├── README.md
├── LICENSE
├── setup.py / pyproject.toml
├── requirements.txt
├── .gitignore
├── docs/
│   ├── GRAM_CARDS.md
│   ├── GROM_LAYOUT.md
│   ├── INTYBASIC_FORMAT.md
│   ├── ASSEMBLY_FORMAT.md
│   ├── PROJECT_REQUIREMENTS.md
│   └── HARDWARE_REFERENCE.md
├── src/
│   └── telligram/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── card.py          # Card data structure
│       │   ├── parser.py        # Input parsers
│       │   ├── validator.py     # Validation logic
│       │   └── converter.py     # Format conversion
│       ├── input/
│       │   ├── __init__.py
│       │   ├── image.py         # Image file handling
│       │   ├── ascii.py         # ASCII art parsing
│       │   ├── binary.py        # Binary data parsing
│       │   └── structured.py    # JSON/YAML parsing
│       ├── output/
│       │   ├── __init__.py
│       │   ├── intybasic.py     # IntyBASIC formatter
│       │   ├── assembly.py      # Assembly formatter
│       │   └── preview.py       # Visual preview
│       └── utils/
│           ├── __init__.py
│           ├── colors.py        # Color processing
│           └── config.py        # Configuration handling
├── tests/
│   ├── __init__.py
│   ├── test_card.py
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_intybasic.py
│   └── test_assembly.py
└── examples/
    ├── sample_card.png
    ├── sprite_sheet.png
    ├── ascii_art.txt
    └── expected_output/
        ├── sample.bas
        └── sample.asm
```

## Development Phases

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
- [ ] Single card extraction
- [ ] Multiple cards from sprite sheet
- [ ] Grid detection

### Phase 3: Advanced Features
- [ ] Assembly hexadecimal output
- [ ] Visual preview in terminal
- [ ] Configuration file support
- [ ] Batch processing
- [ ] Animation frame support
- [ ] Template system

### Phase 4: Polish
- [ ] Interactive mode
- [ ] Comprehensive documentation
- [ ] Example library
- [ ] Performance optimization
- [ ] Cross-platform testing
- [ ] Package distribution (PyPI)

## Dependencies

### Required
- Python 3.8+
- Pillow (PIL) - Image processing
- Click or argparse - CLI framework
- PyYAML - Configuration files

### Optional
- Rich - Terminal formatting and preview
- colorama - Cross-platform color support
- numpy - Image processing optimization

## Quality Assurance

### Testing
- Unit tests for all core components
- Integration tests for CLI
- Example-based tests (known good outputs)
- Cross-platform testing (Windows, macOS, Linux)

### Documentation
- Comprehensive README
- API documentation
- Usage examples
- Tutorial for common workflows
- Reference documentation (this folder)

### Code Quality
- Type hints (Python 3.8+)
- Docstrings (Google or NumPy style)
- Linting (flake8, pylint)
- Formatting (black)
- Static analysis (mypy)

## Success Criteria

The project is considered successful when:

1. ✅ Users can convert 8×8 images to IntyBASIC BITMAP format
2. ✅ Users can convert 8×8 images to Assembly DECLE format
3. ✅ Tool validates 2-color constraint
4. ✅ Tool handles sprite sheets (multiple cards)
5. ✅ Output is ready to use in Intellivision projects
6. ✅ Documentation is clear and complete
7. ✅ Examples cover common use cases
8. ✅ Tests provide good coverage
9. ✅ Package is installable via pip
10. ✅ CLI is intuitive and user-friendly

## Future Enhancements

- Web-based version (browser tool)
- GUI application (PyQt/Tkinter)
- Plugin system for custom formats
- Integration with development environments
- Cloud storage integration
- Collaborative editing features
- Mobile app version
- Real-time Intellivision emulator preview
- GROM character reference/lookup
- Optimize GRAM usage by detecting GROM duplicates
