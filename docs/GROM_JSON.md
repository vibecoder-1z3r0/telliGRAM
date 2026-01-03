# GROM.json File Format

## Overview

GROM.json contains the Graphics ROM character data for the Intellivision. This file enables the **GROM Viewer** tab in telliGRAM, which allows you to:

- Browse all 256 GROM characters
- Copy GROM characters to GRAM slots for editing
- Reference available built-in graphics

## File Format

GROM.json uses a **sparse object format** - you only define the cards you need:

```json
{
  "0": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  "33": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00],
  "65": [0x10, 0x28, 0x44, 0x44, 0x7C, 0x44, 0x44, 0x00]
}
```

**Key points:**
- Card numbers are **strings** (JSON object keys must be strings)
- Valid range: `"0"` to `"255"` (256 cards total)
- Each card is an **array of 8 bytes** (one byte per row, top to bottom)
- Undefined cards are automatically filled with blank data `[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]`

## Byte Value Formats

Each byte can be specified in **multiple formats** - use whichever is most convenient:

### Decimal Integer
```json
"33": [24, 36, 66, 66, 126, 66, 66, 0]
```

### Hexadecimal (with `0x` prefix)
```json
"33": ["0x18", "0x24", "0x42", "0x42", "0x7E", "0x42", "0x42", "0x00"]
```

### Hexadecimal (without prefix, 1-2 hex digits)
```json
"33": ["18", "24", "42", "42", "7E", "42", "42", "00"]
```

### Binary (with `0b` prefix)
```json
"33": ["0b00011000", "0b00100100", "0b01000010", "0b01000010", "0b01111110", "0b01000010", "0b01000010", "0b00000000"]
```

### Binary (without prefix, exactly 8 characters)
```json
"33": ["00011000", "00100100", "01000010", "01000010", "01111110", "01000010", "01000010", "00000000"]
```

### Decimal String
```json
"33": ["24", "36", "66", "66", "126", "66", "66", "0"]
```

### Visual Format (IntyBASIC BITMAP style)
**NEW**: The most visual and intuitive format! Draw characters using ASCII art where:
- `'0'`, `'_'`, `' '` (space), `'.'` = pixel OFF (0)
- **Everything else** = pixel ON (1)

```json
"33": [
  "..XXX...",
  ".X...X..",
  "X.....X.",
  "X.....X.",
  "XXXXXXX.",
  "X.....X.",
  "X.....X.",
  "........"
]
```

You can use any characters you want for pixels! These are all equivalent:
```json
"33": ["..XXX...", ".X...X..", "X.....X.", ...]   // X for pixel
"33": ["..###...", ".#...#..", "#.....#.", ...]   // # for pixel
"33": ["  XXX   ", " X   X  ", "X     X ", ...]   // Space for off
"33": ["__XXX___", "_X___X__", "X_____X_", ...]   // Underscore for off
"33": ["00ABC000", "0D000E00", "F00000G0", ...]   // Any char for on!
```

**Pro tip**: This matches IntyBASIC's `BITMAP` directive syntax!

### Mixed Formats (in same card!)
```json
"33": [24, "0x24", "42", "0b01000010", "7E", "0x42", 66, "0x00"]
```

You can even mix visual format with numeric formats:
```json
"33": ["..XXX...", ".X...X..", 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00]
```

## Complete Example

Here's a minimal GROM.json with ASCII characters 0-94 (space through `~`):

### Numeric Format (Hex)
```json
{
  "0": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  "1": [0x10, 0x10, 0x10, 0x10, 0x10, 0x00, 0x10, 0x00],
  "33": [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00],
  "65": [0x10, 0x28, 0x44, 0x44, 0x7C, 0x44, 0x44, 0x00]
}
```

### Visual Format (Recommended!)
```json
{
  "0": ["........", "........", "........", "........", "........", "........", "........", "........"],
  "1": ["...X....", "...X....", "...X....", "...X....", "...X....", "........", "...X....", "........"],
  "33": ["..XXX...", ".X...X..", "X.....X.", "X.....X.", "XXXXXXX.", "X.....X.", "X.....X.", "........"],
  "48": ["..XXX...", ".X...X..", "X.....X.", "X.....X.", "X.....X.", "X.....X.", ".X...X..", "..XXX..."],
  "65": ["...X....", "..X.X...", ".X...X..", ".X...X..", "XXXXX...", ".X...X..", ".X...X..", "........"]
}
```

**Note:** Cards 95-255 will be blank unless you define them. Different Intellivision EXEC ROM versions have different graphics in this range.

## Understanding Card Data

Each card is 8×8 pixels. Each byte represents one row of 8 pixels:

```
Letter 'A' (Card 33):
Byte  Hex   Binary      Visual
0:    0x18  00011000    ..XXX...
1:    0x24  00100100    .X...X..
2:    0x42  01000010    X.....X.
3:    0x42  01000010    X.....X.
4:    0x7E  01111110    XXXXXXX.
5:    0x42  01000010    X.....X.
6:    0x42  01000010    X.....X.
7:    0x00  00000000    ........
```

**Bit mapping:** Bit 7 = leftmost pixel, Bit 0 = rightmost pixel
- `1` = pixel ON (foreground color)
- `0` = pixel OFF (background/transparent)

## Creating Your GROM.json

### Option 1: Manual Creation

1. Create a text file named `GROM.json`
2. Start with a minimal set (just ASCII 0-94):
   ```json
   {
     "0": [0, 0, 0, 0, 0, 0, 0, 0],
     "33": [24, 36, 66, 66, 126, 66, 66, 0]
   }
   ```
3. Add more cards as needed
4. Use the format that's easiest for you (hex, binary, decimal)

### Option 2: Extract from EXEC ROM

If you have an Intellivision EXEC ROM dump:

1. **Find GROM data** - Located at `$D000-$DFFF` in EXEC ROM
2. **Extract 256 cards** - 2048 bytes total (256 cards × 8 bytes each)
3. **Convert to JSON** - Write a script to convert binary to JSON format

Example Python script:
```python
import json

def rom_to_grom_json(rom_file, output_file):
    with open(rom_file, 'rb') as f:
        # Seek to GROM location (offset depends on ROM dump format)
        f.seek(GROM_OFFSET)
        grom_data = f.read(2048)  # 256 cards × 8 bytes

    grom_json = {}
    for card_num in range(256):
        offset = card_num * 8
        card_bytes = list(grom_data[offset:offset+8])
        grom_json[str(card_num)] = card_bytes

    with open(output_file, 'w') as f:
        json.dump(grom_json, f, indent=2)

rom_to_grom_json('exec.bin', 'GROM.json')
```

### Option 3: Use Existing Dumps

Look for existing GROM dumps in Intellivision emulator/development communities. Common sources:
- Intellivision development forums
- INTV Funhouse
- jzIntv emulator data files

## Usage

### Command Line

```bash
telligram --grom path/to/GROM.json
```

**Examples:**
```bash
# Absolute path
telligram --grom /home/user/intv/GROM.json

# Relative path
telligram --grom ./GROM.json

# Different directory
telligram --grom ~/Documents/intellivision/GROM.json
```

### Without GROM File

If you don't provide `--grom`, the GROM Viewer tab will not appear. You can still use telliGRAM for GRAM card creation and animation.

## Validation and Warnings

telliGRAM validates your GROM.json and prints warnings for issues:

### Valid Card Numbers (0-255)
```
✓ "0", "33", "255" - Valid
✗ "-1", "256", "999" - Out of bounds (ignored with WARNING)
✗ "foo", "ABC" - Non-numeric (ignored with WARNING)
```

### Valid Card Data (array of 8 bytes)
```
✓ [24, 36, 66, 66, 126, 66, 66, 0] - Valid
✗ [24, 36, 66] - Wrong length (ignored with WARNING)
✗ "00011000" - Not an array (ignored with WARNING)
✗ [24, 36, 256, 66, 126, 66, 66, 0] - Byte out of range (ignored with WARNING)
```

### Invalid Bytes
Each byte must be 0-255:
```
✓ 24, "0x18", "00011000" - Valid
✗ 256, "invalid", "XYZ" - Invalid (ignored with WARNING)
```

**Result:** Invalid entries are **silently ignored** (with console WARNING). Valid entries are loaded. Undefined cards become blank.

## ASCII Mapping Reference

Cards 0-94 map to ASCII characters 32-126:

```
Card = ASCII_code - 32
ASCII_code = Card + 32
```

**Quick reference:**
```
Card 0:  (space)
Card 16: '0'
Card 17: '1'
...
Card 25: '9'
Card 33: 'A'
Card 34: 'B'
...
Card 58: 'Z'
Card 65: 'a'
...
Card 90: 'z'
```

## Extended Characters (Cards 95-255)

**IMPORTANT:** Extended character definitions vary by EXEC ROM version!

- **EXEC 1 (1979)** - Different extended graphics
- **EXEC 2 (1982)** - Different extended graphics
- **ECS GROM** - Enhanced Computer System has different characters

**Recommendation:** Extract GROM data from your target EXEC ROM to ensure compatibility.

## Tips

1. **Start small** - Only define cards you need (ASCII 0-94 is ~800 lines)
2. **Use visual format** - The visual ASCII-art format (`"..XXX..."`) is the easiest to read and edit
3. **Use comments** - JSON doesn't support comments, but you can use a build script to strip them
4. **Version control** - Track your GROM.json in Git for different ROM versions
5. **Test incrementally** - Load in telliGRAM frequently to verify correctness
6. **IntyBASIC users** - Visual format matches BITMAP directive syntax perfectly
7. **Mix formats** - Use visual for complex characters, hex/decimal for simple ones

## Troubleshooting

### GROM tab doesn't appear
- Check you're using `--grom path/to/file.json`
- Verify path is correct (absolute or relative to working directory)
- Check console for error messages

### "FileNotFoundError"
- Path to GROM.json is incorrect
- Use absolute path: `--grom /full/path/to/GROM.json`

### "Invalid GROM.json format"
- File is not valid JSON - check syntax
- Make sure it's an object `{}`, not an array `[]`
- Validate JSON with: `python -m json.tool GROM.json`

### Cards appear blank in viewer
- Card numbers might be out of bounds or invalid
- Check console for WARNING messages
- Verify card data has 8 bytes, all 0-255

### "WARNING: Ignoring..."
- Non-critical - indicates invalid data that was skipped
- Check card number is 0-255
- Check card data is array of 8 valid bytes

## Example Files

### Minimal ASCII-only (cards 0-94)
See `examples/GROM_ASCII.json` (create this file with ASCII characters)

### Full EXEC ROM dump (all 256 cards)
See `examples/GROM_FULL.json` (extract from your EXEC ROM)

## References

- [GROM Layout Reference](GROM_LAYOUT.md) - Detailed GROM character map
- [Hardware Reference](HARDWARE_REFERENCE.md) - Intellivision technical specs
- [Intellivision Wiki - Graphics ROM](https://wiki.intellivision.us/index.php/Graphics_ROM)

## License Note

**IMPORTANT:** GROM data from Intellivision EXEC ROM is copyrighted by Intellivision Entertainment. Only use GROM dumps you have legal rights to (e.g., from ROMs you own).

For homebrew development, you can create your own custom GROM.json with original graphics.
