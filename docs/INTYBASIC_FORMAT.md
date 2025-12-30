# IntyBASIC GRAM Card Format

## Overview

IntyBASIC is a BASIC-like high-level language for Intellivision development. It provides a simple, human-readable format for defining GRAM cards using the `BITMAP` statement.

## Syntax

### Basic Card Definition

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

### Character Convention
- **`X` or any non-space/dot:** Pixel ON (1)
- **`.` or space:** Pixel OFF (0)
- **String length:** Must be exactly 8 characters
- **Total rows:** Must be exactly 8 `BITMAP` statements per card

### Multiple Cards

```basic
' Define multiple cards sequentially
player_sprites:
    ' Card 1 - Player facing right
    BITMAP "..XXX..."
    BITMAP ".X...X.."
    BITMAP "X.....X."
    BITMAP "X..X..X."
    BITMAP "X.....X."
    BITMAP ".X...X.."
    BITMAP "..XXX..."
    BITMAP "........"

    ' Card 2 - Player facing left
    BITMAP "...XXX.."
    BITMAP "..X...X."
    BITMAP ".X.....X"
    BITMAP ".X..X..X"
    BITMAP ".X.....X"
    BITMAP "..X...X."
    BITMAP "...XXX.."
    BITMAP "........"
```

## Loading GRAM Cards

### The DEFINE Statement

```basic
DEFINE slot, count, label
```

**Parameters:**
- `slot`: GRAM slot number (0-63)
- `count`: Number of consecutive cards to load
- `label`: Label of the BITMAP data to load

**Card numbering:**
- GRAM slot 0 → Card #256
- GRAM slot 1 → Card #257
- ...
- GRAM slot 63 → Card #319

### Example Usage

```basic
' Define graphics data
ship_gfx:
    BITMAP "..XXXX.."
    BITMAP ".XXXXXX."
    BITMAP "XXXXXXXX"
    BITMAP "XX.XX.XX"
    BITMAP "X..XX..X"
    BITMAP "....XX.."
    BITMAP "...X..X."
    BITMAP "...X..X."

' Load to GRAM slot 0 (card #256)
DEFINE 0, 1, ship_gfx
WAIT                    ' Synchronize with display
```

### Loading Multiple Cards

```basic
' Define 4 animation frames
walk_cycle:
    ' Frame 1
    BITMAP "..XXX..."
    BITMAP ".X...X.."
    BITMAP "X.....X."
    BITMAP "X..X..X."
    BITMAP "X.....X."
    BITMAP ".X...X.."
    BITMAP "..X.X..."
    BITMAP "...X...."

    ' Frame 2
    BITMAP "..XXX..."
    BITMAP ".X...X.."
    BITMAP "X.....X."
    BITMAP "X..X..X."
    BITMAP "X.....X."
    BITMAP ".X...X.."
    BITMAP "...X...."
    BITMAP "..X.X..."

    ' ... frames 3 and 4 ...

' Load all 4 cards starting at slot 0
DEFINE 0, 4, walk_cycle
WAIT
```

## Using GRAM Cards

### In Sprites (SPRITE Statement)

```basic
' SPRITE number, x, y, card
SPRITE 0, x + $300, y + $200, 256 + color
'              ^         ^      ^
'              |         |      |
'         interaction  1x     GRAM
'         + visible   scale   card 256
```

### In Background (PRINT Statement)

```basic
' Print GRAM card to screen
PRINT AT position, "\256"    ' Prints card #256
PRINT AT position, "\257"    ' Prints card #257

' Using variables
card = 256
PRINT AT position, CHR$(card)
```

### In SCREEN Statement

```basic
' Define screen layout with GRAM cards
SCREEN
    DATA 256, 257, 258    ' Use GRAM cards in screen data
    ' ...
```

## Performance Constraints

### Loading Limits
- **Maximum ~18 cards per frame** (NTSC, 60 Hz)
- **Reduced with sound:**
  - 16 cards/frame with `PLAY` statement
  - 13 cards/frame with `PLAY FULL`

### The WAIT Statement
```basic
DEFINE 0, 4, sprite_data
WAIT    ' CRITICAL: Synchronize with VBLANK before using cards
```

**Why WAIT is necessary:**
- GRAM updates happen during VBLANK period
- Without WAIT, graphics may not be loaded yet
- Always WAIT after DEFINE before using the cards

## Best Practices

### 1. Pre-load Static Graphics
```basic
' Load all graphics during initialization
DEFINE 0, 10, game_sprites
WAIT
DEFINE 10, 8, level_tiles
WAIT
DEFINE 18, 4, ui_elements
WAIT
```

### 2. Use Descriptive Labels
```basic
' Good
player_walk_right:
    BITMAP "..XXXX.."
    ' ...

' Bad
gfx1:
    BITMAP "..XXXX.."
    ' ...
```

### 3. Group Related Graphics
```basic
' Animation frames together
player_animations:
    ' Walk cycle
    BITMAP "..." ' Frame 1
    ' ...
    BITMAP "..." ' Frame 2
    ' ...
    BITMAP "..." ' Frame 3
    ' ...
    BITMAP "..." ' Frame 4
    ' ...
```

### 4. Comment Your Graphics
```basic
' Player ship - small (8x8)
player_ship:
    BITMAP "...XX..."    ' Nose
    BITMAP "..XXXX.."    ' Cockpit
    BITMAP ".XXXXXX."    ' Body
    BITMAP "XXXXXXXX"    ' Wings
    BITMAP "XX.XX.XX"    ' Wing details
    BITMAP "X..XX..X"    ' Engine vents
    BITMAP "....XX.."    ' Exhaust
    BITMAP "...X..X."    ' Flame
```

## Example: Complete Usage

```basic
REM Complete example of GRAM card usage

' Define graphics
ship_gfx:
    BITMAP "..XXXX.."
    BITMAP ".XXXXXX."
    BITMAP "XXXXXXXX"
    BITMAP "XX.XX.XX"
    BITMAP "X..XX..X"
    BITMAP "....XX.."
    BITMAP "...X..X."
    BITMAP "...X..X."

bullet_gfx:
    BITMAP "...XX..."
    BITMAP "..XXXX.."
    BITMAP "..XXXX.."
    BITMAP "...XX..."
    BITMAP "........"
    BITMAP "........"
    BITMAP "........"
    BITMAP "........"

' Main program
CLS
DEFINE 0, 1, ship_gfx      ' Load ship to slot 0 (card 256)
WAIT
DEFINE 1, 1, bullet_gfx    ' Load bullet to slot 1 (card 257)
WAIT

' Use in game
x = 80
y = 50
SPRITE 0, x + $300, y + $200, 256 + 7    ' White ship

' Fire bullet
bullet_x = x
bullet_y = y - 10
SPRITE 1, bullet_x + $300, bullet_y + $200, 257 + 6    ' Yellow bullet
```

## Character Variations

Different developers use different characters for pixel representation:

### Common Conventions
```basic
' Using X and .
BITMAP "XX....XX"

' Using # and .
BITMAP "##....##"

' Using 1 and 0
BITMAP "11....11"

' Using @ and space
BITMAP "@@    @@"
```

**IntyBASIC accepts any non-space character as "pixel on"**

## telliGRAM Output Format

For telliGRAM, we'll use the standard convention:

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

- **Pixel ON:** `X`
- **Pixel OFF:** `.`
- **Consistent formatting** for readability

## References

- IntyBASIC Quick Reference (provided by user)
- [IntyBASIC Documentation](https://nanochess.org/intybasic.html)
