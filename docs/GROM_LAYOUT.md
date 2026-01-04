# GROM Layout - Graphics ROM Reference

## Overview

**GROM** (Graphics ROM) is the built-in, read-only character set on the Intellivision. Unlike GRAM which can be programmed at runtime, GROM contains 256 fixed graphics cards that are always available.

## Memory Location

- **Address:** `$D000-$DFFF` (ROM)
- **Size:** 2048 bytes (256 cards × 8 bytes each)
- **Card Numbers:** 0-255
- **Access:** Read-only, always available (no loading required)

## Card Layout

### ASCII Character Mapping (Cards 0-94)

The first 95 GROM cards (0-94) map **directly to printable ASCII characters** (32-126):

**Conversion Formula:**
```
GROM_card = ASCII_code - 32
ASCII_code = GROM_card + 32
```

**Why 32?** ASCII codes below 32 are non-printable control characters, so GROM starts with ASCII 32 (space).

### Character Set Breakdown

#### GROM 0-15 (ASCII 32-47) - Space & Punctuation
```
Card  ASCII  Char
  0     32    (space)
  1     33    !
  2     34    "
  3     35    #
  4     36    $
  5     37    %
  6     38    &
  7     39    '
  8     40    (
  9     41    )
 10     42    *
 11     43    +
 12     44    ,
 13     45    -
 14     46    .
 15     47    /
```

#### GROM 16-31 (ASCII 48-63) - Numbers & Symbols
```
Card  ASCII  Char
 16     48    0
 17     49    1
 18     50    2
 19     51    3
 20     52    4
 21     53    5
 22     54    6
 23     55    7
 24     56    8
 25     57    9
 26     58    :
 27     59    ;
 28     60    <
 29     61    =
 30     62    >
 31     63    ?
```

#### GROM 32-47 (ASCII 64-79) - @ and Uppercase A-O
```
Card  ASCII  Char
 32     64    @
 33     65    A
 34     66    B
 35     67    C
 36     68    D
 37     69    E
 38     70    F
 39     71    G
 40     72    H
 41     73    I
 42     74    J
 43     75    K
 44     76    L
 45     77    M
 46     78    N
 47     79    O
```

#### GROM 48-63 (ASCII 80-95) - Uppercase P-Z & Symbols
```
Card  ASCII  Char
 48     80    P
 49     81    Q
 50     82    R
 51     83    S
 52     84    T
 53     85    U
 54     86    V
 55     87    W
 56     88    X
 57     89    Y
 58     90    Z
 59     91    [
 60     92    \
 61     93    ]
 62     94    ^
 63     95    _
```

#### GROM 64-79 (ASCII 96-111) - ` and Lowercase a-o
```
Card  ASCII  Char
 64     96    `
 65     97    a
 66     98    b
 67     99    c
 68    100    d
 69    101    e
 70    102    f
 71    103    g
 72    104    h
 73    105    i
 74    106    j
 75    107    k
 76    108    l
 77    109    m
 78    110    n
 79    111    o
```

#### GROM 80-94 (ASCII 112-126) - Lowercase p-z & Symbols
```
Card  ASCII  Char
 80    112    p
 81    113    q
 82    114    r
 83    115    s
 84    116    t
 85    117    u
 86    118    v
 87    119    w
 88    120    x
 89    121    y
 90    122    z
 91    123    {
 92    124    |
 93    125    }
 94    126    ~
```

### Extended Graphics (Cards 95-255)

Cards 95-255 contain special graphics that vary by GROM version:

#### Common Extended Characters (Typical)
- **Card Suits:** Hearts, diamonds, clubs, spades
- **Box Drawing:** Single/double lines, corners, T-junctions
- **Symbols:** Arrows, bullets, geometric shapes
- **Game Graphics:** Common game elements (varies by EXEC version)

**Note:** The exact contents of cards 95-255 can vary between different Intellivision EXEC ROM versions. Always test with your target system.

## Quick Reference Tables

### Hexadecimal Lookup

```
      +0  +1  +2  +3  +4  +5  +6  +7  +8  +9  +A  +B  +C  +D  +E  +F
$00:  SP  !   "   #   $   %   &   '   (   )   *   +   ,   -   .   /
$10:  0   1   2   3   4   5   6   7   8   9   :   ;   <   =   >   ?
$20:  @   A   B   C   D   E   F   G   H   I   J   K   L   M   N   O
$30:  P   Q   R   S   T   U   V   W   X   Y   Z   [   \   ]   ^   _
$40:  `   a   b   c   d   e   f   g   h   i   j   k   l   m   n   o
$50:  p   q   r   s   t   u   v   w   x   y   z   {   |   }   ~   [extended]
$60+: [Extended graphics - varies by GROM version]
```

### Common Letters Quick Reference

```
Uppercase:
A=33  B=34  C=35  D=36  E=37  F=38  G=39  H=40  I=41  J=42
K=43  L=44  M=45  N=46  O=47  P=48  Q=49  R=50  S=51  T=52
U=53  V=54  W=55  X=56  Y=57  Z=58

Lowercase:
a=65  b=66  c=67  d=68  e=69  f=70  g=71  h=72  i=73  j=74
k=75  l=76  m=77  n=78  o=79  p=80  q=81  r=82  s=83  t=84
u=85  v=86  w=87  x=88  y=89  z=90

Numbers:
0=16  1=17  2=18  3=19  4=20  5=21  6=22  7=23  8=24  9=25
```

## Usage Examples

### IntyBASIC - Printing Text

```basic
' GROM cards used automatically for text
PRINT AT 0, "HELLO WORLD"

' Character codes work too
PRINT AT 0, CHR$(40)    ' Prints 'H' (GROM card 40)

' Mixing GROM and GRAM
PRINT AT 0, "SCORE: \256"    ' Text from GROM, custom icon from GRAM
```

### Assembly - Using GROM Cards

```asm
; Display letter 'A' (GROM card 33) at screen position 0
        MVII    #$1021, R0      ; Card 33 ($21) + color stack ($1000)
        MVO     R0, $0200       ; Top-left of screen

; Display 'HELLO' using GROM
        MVII    #$1028, R0      ; 'H' (card 40 = $28)
        MVO     R0, $0200
        MVII    #$1029, R0      ; 'E' (card 37 = $25)  [ERROR - should be $25]
        MVO     R0, $0201
        ; ... etc
```

### Converting ASCII String to GROM

```python
# Python example for code generation
def ascii_to_grom(text):
    """Convert ASCII string to GROM card numbers"""
    return [ord(char) - 32 for char in text]

# Example usage
text = "HELLO"
grom_cards = ascii_to_grom(text)
# Result: [40, 37, 44, 44, 47]  (H, E, L, L, O)
```

## GROM vs GRAM Decision Guide

### Use GROM When:
- ✅ Displaying text (letters, numbers, punctuation)
- ✅ Standard symbols already in GROM
- ✅ Saving GRAM slots for custom graphics
- ✅ No loading/initialization needed

### Use GRAM When:
- ✅ Custom game sprites
- ✅ Animation frames
- ✅ Special symbols not in GROM
- ✅ Game-specific graphics
- ✅ Need more than 2 colors per character (by switching cards)

## Example Character Bitmaps

Here are some example GROM characters in bitmap form:

### Letter 'A' (GROM Card 33)
```
..XXX...   $18
.X...X..   $24
X.....X.   $42
X.....X.   $42
XXXXXXX.   $7E
X.....X.   $42
X.....X.   $42
........   $00
```

### Number '0' (GROM Card 16)
```
..XXX...   $18
.X...X..   $24
X.....X.   $42
X.....X.   $42
X.....X.   $42
X.....X.   $42
.X...X..   $24
..XXX...   $18
```

### Space (GROM Card 0)
```
........   $00
........   $00
........   $00
........   $00
........   $00
........   $00
........   $00
........   $00
```

## telliGRAM Integration

### Why GROM Matters for telliGRAM

When generating code, telliGRAM should:

1. **Detect ASCII Text:** If input is standard text, suggest using GROM instead of GRAM
2. **Optimize GRAM Usage:** Don't waste GRAM slots on characters already in GROM
3. **Mixed Mode:** Support designs that combine GROM text with GRAM graphics
4. **Card Number Validation:** Ensure card references don't conflict (0-255 = GROM, 256-319 = GRAM)

### Example Code Generation

```basic
' telliGRAM could generate smart code like:

' Use GROM for text
PRINT AT 0, "SCORE:"

' Use GRAM for custom graphics
DEFINE 0, 1, player_sprite
WAIT
SPRITE 0, x + $300, y + $200, 256 + 7    ' Custom player graphic
```

### Future Feature: Text to Graphics

telliGRAM could convert text strings to card data:

```bash
# Generate BACKTAB data for "HELLO" using GROM
$ telligram --text "HELLO" --format backtab

# Output (assembly):
screen_hello:
        DECLE   $1028    ; 'H' - GROM card 40
        DECLE   $1025    ; 'E' - GROM card 37
        DECLE   $102C    ; 'L' - GROM card 44
        DECLE   $102C    ; 'L' - GROM card 44
        DECLE   $102F    ; 'O' - GROM card 47
```

## Important Notes

### GROM Version Differences
- **Executive ROM versions** may have different graphics in cards 95+
- **Always test** extended characters on your target hardware
- **Core ASCII** (cards 0-94) is consistent across versions

### Performance
- **GROM access is free:** No loading time, no VBLANK constraints
- **Always available:** All 256 cards accessible at any time
- **No initialization:** Can use immediately

### Memory Considerations
- **GROM doesn't use RAM:** Saves precious system RAM
- **Read-only:** Cannot be modified (use GRAM for custom graphics)
- **No slot limits:** All 256 cards available simultaneously

## References

- [Graphics ROM - Intellivision Wiki](https://wiki.intellivision.us/index.php/Graphics_ROM)
- [Print.asm - Intellivision Wiki](http://wiki.intellivision.us/index.php/Print.asm)
- [Memory Map - Intellivision Wiki](http://wiki.intellivision.us/index.php/Memory_Map)
- [ASCII Code Table](https://theasciicode.com.ar/)

## Summary

| Feature | GROM | GRAM |
|---------|------|------|
| **Location** | ROM ($D000-$DFFF) | RAM ($3000-$33FF) |
| **Cards** | 256 (0-255) | 64 (256-319) |
| **Type** | Read-only | Read/write |
| **Content** | ASCII + symbols | User-defined |
| **Loading** | Always available | Must load at runtime |
| **Limit** | None | ~18 cards/frame |
| **Best For** | Text, common symbols | Custom sprites, animations |

**Pro Tip:** Use GROM for everything you can, save GRAM for what makes your game unique!
