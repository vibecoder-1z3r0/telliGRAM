# STIC Figures - Design & Architecture

**Full-screen designer for Intellivision BACKTAB and MOB composition**

---

## Overview

STIC Figures is a visual tool for designing complete Intellivision screens, including:
- **BACKTAB**: 20×12 background tile grid (240 tiles)
- **MOBs**: 8 movable sprites with full configuration
- **Color management**: Color Stack or Foreground/Background modes
- **Border control**: Color, visibility, and masking
- **Export**: Generate IntyBASIC, Assembly, or MBCC code

---

## Technical Specifications

### BACKTAB (Background Table)

**Memory Location:** `$0200-$035F` (240 16-bit words)

**Grid:** 20 columns × 12 rows = 240 tiles
- Each tile: 8×8 pixels
- Total playfield: 160×96 pixels

**Screen Coordinates:**
```
Full screen: 176×112 pixels (with 8px border on all sides)

Border (8px) ┌────────────────────────────────────┐
             │  BACKTAB playfield (160×96)        │
             │  Card (0,0) at screen (8,8)        │
             │  Card (19,11) at screen (159,95)   │
             └────────────────────────────────────┘

Coordinate conversion:
  Screen X = 8 + (col × 8)
  Screen Y = 8 + (row × 8)

  BACKTAB address = $0200 + (row × 20) + col
```

---

### BACKTAB Entry Format

**Two modes available (global setting):**

#### Mode 1: Color Stack Mode (Default)

**Register $0020 bit 1 = 0**

Each BACKTAB entry (16 bits):
```
Bit   15 14 13 12 11 10 09 08 07 06 05 04 03 02 01 00
      ├──┼──┼──┼──┴──┴──┴──┴──┴──┴──┴──┼──┴──┴──┴──┘
      │  │  │  │                       │
      │  │  │  │                       └─ FG color (bits 0-2, low 3 bits)
      │  │  │  │
      │  │  │  └───────────────────────── FG color bit 3 (high bit)
      │  │  │
      │  │  └──────────────────────────── Advance color stack (after drawing)
      │  │
      │  └─────────────────────────────── (unused)
      │
      └────────────────────────────────── (unused)

Bits 3-11: Card number (0-511)
  0-255:   GROM cards
  256-319: GRAM cards (64 total)
  320-511: Extended (future use)
```

**Color Stack Registers:**
- `$0021`: Stack slot 0 (initial background color)
- `$0022`: Stack slot 1
- `$0023`: Stack slot 2
- `$0024`: Stack slot 3

**Stack Behavior:**
- Current position starts at slot 0
- Tiles use current stack color for background pixels
- When bit 13 set: **AFTER** drawing tile, advance to next slot
- Stack wraps: 0→1→2→3→0

**Example:**
```
Stack: Slot 0=Blue, Slot 1=Brown, Slot 2=Black, Slot 3=Green
Current: Slot 0 (Blue)

Tile A: Card 65 ('A'), FG=White, Adv=0
  → White 'A' on Blue background
  → Stack stays at 0

Tile B: Card 66 ('B'), FG=Yellow, Adv=1
  → Yellow 'B' on Blue background
  → Stack advances to 1

Tile C: Card 67 ('C'), FG=White, Adv=0
  → White 'C' on Brown background (slot 1)
  → Stack stays at 1
```

#### Mode 2: Foreground/Background Mode

**Register $0020 bit 1 = 1**

Each BACKTAB entry specifies both foreground AND background colors:
```
Bit   15 14 13 12 11 10 09 08 07 06 05 04 03 02 01 00
      ├──┼──┼──┼──┴──┴──┴──┴──┴──┴──┴──┼──┴──┴──┴──┘
      │  │  │  │                       │
      │  │  │  │                       └─ FG color (bits 0-2)
      │  │  │  │
      │  │  │  └───────────────────────── FG color bit 3
      │  │  │
      │  │  └──────────────────────────── BG color bit 3
      │  │
      │  └─────────────────────────────── BG color (bits 0-2)
      │
      └────────────────────────────────── (mode bit, set by $0020)

Bits 3-11: Card number (0-511)
```

**No color stack in this mode** - each tile is self-contained.

**Mode Selection:**
- Per STIC Figure setting (not per-tile)
- Entire BACKTAB uses one mode
- Most games use Color Stack mode

---

### Border

**Registers:**
- `$002C`: Border color (0-15)
- `$0030`: Border mask
  - Bit 0: Disable left border (8px)
  - Bit 1: Disable top border (8px)
  - Right and bottom borders always visible

**Border Size:** 8 pixels on all sides

**Purpose:**
1. Visual frame around playfield
2. Smooth scrolling buffer (reveals next tiles during scroll)

**Border Visibility Options:**
- Master on/off toggle
- Independent left/top disable
- Color selection (16 colors)

---

### Card Numbering

**Card Ranges:**
- **0-255**: GROM (Graphics ROM)
  - Built-in character graphics
  - Loaded from GROM.json file
  - Examples: ASCII characters, symbols

- **256-319**: GRAM (Graphics RAM)
  - User-defined cards (64 total)
  - Card 256 = GRAM slot 0
  - Card 319 = GRAM slot 63
  - Source: Current project's GRAM cards

**Card Data Format:**
- 8 bytes per card (one byte per row)
- Each byte: 8 pixels (bit 7 = leftmost, bit 0 = rightmost)
- Bit 1 = foreground pixel, Bit 0 = background pixel

---

### MOBs (Movable Object Blocks)

**8 MOBs total**, each with 3 registers:

#### X Position Register ($0000-$0007)
```
Bits 0-7:  X coordinate (0-168 visible range)
Bit 8:     Interaction (collision detection enable)
Bit 9:     Visibility
Bit 10:    Double width (2×)

Common: X_pos + $300 (visible + interaction)
```

#### Y Position Register ($0008-$000F)
```
Bits 0-6:  Y coordinate (0-95 visible range)
Bit 7:     Double height (16 lines vs 8)
Bits 8-9:  Scale (00=×0.5, 01=×1, 10=×2, 11=×4)
Bit 10:    Flip horizontal
Bit 11:    Flip vertical

Common: Y_pos + $200 (1× scale)
```

#### Attribute Register ($0010-$0017)
```
Bits 0-2:  Color (low 3 bits)
Bits 3-11: Card number (0-319)
Bit 12:    Color bit 3 (high bit, makes 4-bit color)
Bit 13:    Priority (0=foreground, 1=background)

Foreground MOBs: Draw over BACKTAB
Background MOBs: BACKTAB draws over them
```

**MOB Features:**
- Position: Pixel-level (not tile-locked)
- Size: Can be scaled independently (width, height, scale)
- Transforms: Flip H/V
- Collision: Hardware collision detection
- Priority: Can be behind or in front of BACKTAB

---

## Data Model

### STIC Figure JSON Structure

```json
{
  "name": "Title Screen",
  "mode": "color_stack",  // or "fg_bg"

  "border": {
    "visible": true,
    "color": 0,
    "show_left": true,
    "show_top": true
  },

  "color_stack": [0, 1, 2, 3],  // Only used in color_stack mode

  "backtab": [
    {
      "row": 0,
      "col": 0,
      "card": 256,
      "fg_color": 7,
      "bg_color": 0,        // Only used in fg_bg mode
      "advance_stack": false // Only used in color_stack mode
    }
    // ... 239 more entries
  ],

  "mobs": [
    {
      "id": 0,
      "visible": true,
      "interaction": true,
      "x": 80,
      "y": 50,
      "card": 256,
      "color": 7,
      "width_2x": false,
      "height_2x": false,
      "scale": 1,  // 0.5, 1, 2, or 4
      "flip_h": false,
      "flip_v": false,
      "priority": "foreground",  // or "background"
      "animation_id": null  // Future: link to animation
    }
    // ... 7 more MOBs
  ]
}
```

---

## Assembly Export Format

### BACKTAB Data (Color Stack Mode)

```asm
; BACKTAB data for "Title Screen"
; 20×12 tiles = 240 words
; Mode: Color Stack

BACKTAB_DATA:
    ; Row 0
    DECLE   $1041      ; Card 65 ('A'), FG=White (7), Adv=0
    DECLE   $1042      ; Card 66 ('B'), FG=White (7), Adv=0
    DECLE   $3043      ; Card 67 ('C'), FG=White (7), Adv=1
    ; ... 17 more columns

    ; Row 1
    DECLE   $2100      ; Card 256 (GRAM 0), FG=Red (2), Adv=0
    ; ... 19 more columns

    ; ... rows 2-11

; Color stack initialization
INIT_COLOR_STACK:
    MVII    #$01, R0        ; Blue
    MVO     R0, $0021       ; Stack slot 0

    MVII    #$03, R0        ; Brown
    MVO     R0, $0022       ; Stack slot 1

    MVII    #$00, R0        ; Black
    MVO     R0, $0023       ; Stack slot 2

    MVII    #$05, R0        ; Green
    MVO     R0, $0024       ; Stack slot 3

    JR      R5

; Border setup
INIT_BORDER:
    MVII    #$00, R0        ; Black
    MVO     R0, $002C       ; Border color

    CLRR    R0              ; Show all borders
    MVO     R0, $0030       ; Border mask

    JR      R5

; Load BACKTAB to screen
LOAD_BACKTAB:
    MVII    #BACKTAB_DATA, R4
    MVII    #$0200, R5      ; BACKTAB start
    MVII    #240, R1        ; 240 tiles

@@loop:
    MVI     @R4, R0
    MVO     R0, @R5
    DECR    R1
    BNEQ    @@loop

    JR      R5
```

### MOB Setup

```asm
; MOB 0: Player sprite
INIT_MOB_0:
    ; X position: 80, visible, interaction
    MVII    #(80 + $300), R0
    MVO     R0, $0000

    ; Y position: 50, 1× scale
    MVII    #(50 + $200), R0
    MVO     R0, $0008

    ; Card 256 (GRAM 0), White (7), Foreground
    MVII    #((256 << 3) + 7), R0
    MVO     R0, $0010

    JR      R5
```

---

## Binary Layout

### BACKTAB Entry Examples

**Card 65 ('A'), White FG, Color Stack, No Advance:**
```
Decimal: 4161
Hex:     $1041
Binary:  0001 0000 0100 0001
         │││└────────────┘└─ FG color: 0111 (7 = White)
         ││└──────────────── Card: 065 ($41)
         │└───────────────── FG bit 3: 0
         └────────────────── Advance: 0

Assembly: DECLE $1041
```

**Card 256 (GRAM 0), Red FG, Advance Stack:**
```
Decimal: 12546
Hex:     $3102
Binary:  0011 0001 0000 0010
         │││└────────────┘└─ FG color: 0010 (2 = Red)
         ││└──────────────── Card: 256 ($100)
         │└───────────────── FG bit 3: 0
         └────────────────── Advance: 1

Assembly: DECLE $3102
```

**Bit-by-bit breakdown:**
```
Position: 15 14 13 12 11 10 09 08 07 06 05 04 03 02 01 00
Value:     0  0  1  1  0  0  0  1  0  0  0  0  0  0  1  0
          ─┬──┴──┬──┬──┴──┴──┴──┴──┴──┴──┴──┴──┬──┴──┴──┴─
           │     │  │                           │
      Unused  Adv │                        FG Color
               FG bit 3                     0010 (Red)

           Card Number: 00100000000 = 256
```

---

## UI Components

### Left Panel: Card Palette (240px)

**Tabs:**
- GRAM (cards 256-319 from project)
- GROM (cards 0-255 from GROM.json)

**Display:**
- Card number (decimal + hex)
- GRAM slot (for GRAM cards)
- 8×8 preview
- Label (if available)

**Selected card indicator:** Blue border

### Center Panel: BACKTAB Canvas

**Rendering layers (bottom to top):**
1. Border (if visible)
2. BACKTAB tiles with foreground + background colors
3. Grid lines (optional)
4. Stack position indicators (small numbers)
5. Selection highlight (bright yellow border)
6. MOBs overlay (if enabled)

**Interactions:**
- Click tile: Select for editing
- Paint tile: Apply selected card + color
- Hover: Show coordinates
- Right-click: Context menu (copy/paste/clear)

**Coordinate display:**
```
Mouse: X: 80  Y: 50        (screen coords)
BACKTAB: Row: 5  Col: 10   (tile coords)
Card: #256 (GRAM Slot 0)   (card info)
```

### Right Panel: Properties (280px)

**Sections:**
1. Display Settings (grid, border)
2. Mode Selection (Color Stack vs FG/BG)
3. Color Stack (4 slots + preview)
4. Selected Tile Properties
5. MOB List/Editor

---

## Color Stack Visualization

**Mini-grid showing stack positions:**
```
┌──────────────────────┐
│ 0 0 0 0 0 0 0 0 0 0  │  ← Slot 0 (Blue)
│ 0 0 0 0 0 0 0 0 0 0  │
│ 0 0 0 1 1 1 1 1 1 1  │  ← Advances at col 3
│ 1 1 1 1 1 1 1 1 1 1  │  ← Slot 1 (Brown)
│ 1 1 1 1 1 2 2 2 2 2  │  ← Advances at col 5
│ 2 2 2 2 2 2 2 2 2 2  │  ← Slot 2 (Black)
└──────────────────────┘

Legend:
0 = Stack slot 0 active
1 = Stack slot 1 active
2 = Stack slot 2 active
3 = Stack slot 3 active
```

---

## Export Formats

### 1. IntyBASIC

```basic
' BACKTAB data
DEFINE BACKTAB_DATA
    DATA $1041, $1042, $3043, ...  ' Row 0
    DATA $2100, $2101, $2102, ...  ' Row 1
    ' ... rows 2-11
END DEFINE

' Color stack
#stack0 = 1  ' Blue
#stack1 = 3  ' Brown
#stack2 = 0  ' Black
#stack3 = 5  ' Green

' Border
#border_color = 0  ' Black

' MOB 0
#mob0x = 80
#mob0y = 50
#mob0a = (256 * 8) + 7  ' Card 256, White
```

### 2. Assembly (.asm)

See Assembly Export Format section above.

### 3. MBCC (Future)

To be defined based on MBCC syntax requirements.

### 4. Raw Binary (.bin)

480 bytes (240 words × 2 bytes) in little-endian format.

---

## Implementation Phases

### Phase 1: Basic BACKTAB Designer
- 20×12 grid canvas
- GRAM/GROM palette
- Click to place cards
- Foreground color selection
- Save/load STIC figures
- Color Stack mode only

### Phase 2: Color Stack
- Color stack UI (4 dropdowns)
- Advance stack checkbox per tile
- Visual stack preview mini-grid
- Stack position indicators on tiles

### Phase 3: Border & Display
- Border settings (visible, color, masks)
- Grid toggle
- Selection highlighting
- Coordinate display

### Phase 4: MOBs
- 8 MOB table view
- MOB editor dialog
- MOB overlay on canvas
- Position, size, transforms

### Phase 5: Export
- IntyBASIC export
- Assembly export
- Binary layout view

### Phase 6: Advanced
- FG/BG mode support
- Multiple figure management
- Import BACKTAB data
- MOB animations

---

## Technical Constraints

**Hardware Limits:**
- BACKTAB: 240 tiles maximum
- MOBs: 8 maximum
- GRAM: 64 cards maximum
- Colors: 16 total (but limited per tile)
- Card range: 0-511 theoretical, 0-319 practical

**VBLANK Constraint:**
- All STIC register writes must occur during VBLANK
- Duration: ~1.3ms (20-25 scanlines)
- Limits how much can be updated per frame

**GRAM Loading:**
- ~18 GRAM cards can be loaded per frame (NTSC)
- Exceeding this causes flicker
- Must plan GRAM usage carefully

---

## References

- Intellivision hardware specs: See `HARDWARE_REFERENCE.md`
- BACKTAB memory map: `$0200-$035F`
- STIC registers: `$0000-$003F` (VBLANK only)
- GROM format: See `GROM_JSON.md`
- Color palette: 16 colors (0-15)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-03
**Status:** Design Phase
