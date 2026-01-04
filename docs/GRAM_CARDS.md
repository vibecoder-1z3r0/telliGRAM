# GRAM Cards - Technical Overview

## What are GRAM Cards?

GRAM (Graphics RAM) cards are user-definable 8×8 pixel graphics characters on the Intellivision console. Unlike GROM (Graphics ROM) which contains fixed built-in graphics, GRAM allows programmers to create custom sprites and background tiles by loading data into specific memory locations.

## Technical Specifications

### Memory Layout
- **Location:** `$3000-$33FF` (or `$0400-$04FF` depending on system configuration)
- **Total Cards:** 64 GRAM cards
- **Card Numbers:** 256-319 (as referenced in code)
- **Total Size:** 512 bytes (64 cards × 8 bytes each)

### Card Structure
Each GRAM card is **8×8 pixels** stored as **8 consecutive bytes**:
- 1 byte per row
- 8 rows per card
- Each bit represents one pixel (1 = on, 0 = off)

### Example Card Layout
```
Card 256 at $3000-$3007:
  $3000: %00011000    ; Row 0:    XX
  $3001: %00100100    ; Row 1:   X  X
  $3002: %01000010    ; Row 2:  X    X
  $3003: %01111110    ; Row 3:  XXXXXX
  $3004: %01000010    ; Row 4:  X    X
  $3005: %01000010    ; Row 5:  X    X
  $3006: %01000010    ; Row 6:  X    X
  $3007: %00000000    ; Row 7:
```

## Color System

### Color Constraints
- **GRAM data is 1-bit:** Only stores pixel on/off
- **Colors defined elsewhere:**
  - For backgrounds: Set in BACKTAB entry
  - For sprites (MOBs): Set in attribute register
- **2 colors per card maximum:** One foreground, one background

### Color Palette
The Intellivision has a 16-color palette:
- **Primary colors (0-7):** Black, Blue, Red, Tan, Dark Green, Green, Yellow, White
- **Pastel colors (8-15):** Brighter variants of 0-7

## Performance Constraints

### Loading Limits
- **Max cards per frame:** ~18 cards (NTSC)
- **Reduced with sound:**
  - 16 cards/frame with PLAY
  - 13 cards/frame with PLAY FULL
- **Why:** Limited CPU cycles during VBLANK period

### Best Practices
1. Pre-load static graphics during initialization
2. Animate by changing card references, not reloading GRAM
3. Reserve GRAM updates for dynamic/essential graphics only
4. Use GROM cards whenever possible to save GRAM slots

## Screen Integration

### BACKTAB (Background)
The screen is a 20×12 grid of cards (240 total positions):
- **Memory:** `$0200-$035F`
- **Position formula:** `$0200 + (row × 20) + column`
- **Resolution:** 160×96 pixels (20 cards × 8 pixels wide, 12 cards × 8 pixels tall)
- **Visible area:** ~159×96 pixels (rightmost column not displayed)

### MOBs (Sprites)
- **Total MOBs:** 8 hardware sprites
- **Attributes:** X position, Y position, Card + Color
- **Scaling:** Can be 0.5×, 1×, 2×, or 4× size
- **Flipping:** Can flip horizontally and/or vertically

## Usage Examples

### Background Tile
```asm
; Load GRAM card 256 to screen position (row 5, col 10)
; Position = $0200 + (5 × 20 + 10) = $0200 + 110 = $026E

MVII #(256 + $1000), R0    ; Card 256 + color stack mode
MVO  R0, $026E             ; Write to BACKTAB
```

### Sprite (MOB)
```asm
; Set MOB 0 to use GRAM card 256 with color 3 (tan)
MVII #(256 + 3), R0        ; Card number + color
MVO  R0, $0010             ; MOB 0 attribute register
```

## References

- [Graphics RAM - Intellivision Wiki](http://wiki.intellivision.us/index.php/Graphics_RAM)
- [STIC - Intellivision Wiki](http://wiki.intellivision.us/index.php?title=STIC)
- [BACKTAB - Intellivision Wiki](http://wiki.intellivision.us/index.php/BACKTAB)
- [Memory Map - Intellivision Wiki](http://wiki.intellivision.us/index.php/Memory_Map)
- [STIC Programming Documentation](http://spatula-city.org/~im14u2c/intv/jzintv-1.0-beta3/doc/programming/stic.txt)
