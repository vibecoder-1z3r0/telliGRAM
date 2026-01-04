# Intellivision Hardware Quick Reference

**For assembly programming and reverse engineering. Keep this in your project for Claude Code to reference.**

## System Overview

- **CPU:** CP1610 @ ~894.886 kHz (NTSC)
- **Graphics:** STIC chip - 8 MOBs (sprites), 20×12 background
- **Sound:** AY-3-8914 PSG - 3 tone + 1 noise channel
- **Display:** 159×96 pixels, 16 colors
- **Memory:** 16-bit words (decles), 64K address space

---

## CP1610 CPU Quick Reference

### Registers
```
R0-R5: General purpose (16-bit)
R6:    Stack Pointer (SP)
R7:    Program Counter (PC)
```

### Essential Instructions
```
MVO  Rn, addr       Store register to memory
MVI  addr, Rn       Load memory to register
MVII #imm, Rn       Load immediate value
MOVR Rm, Rn         Copy register

ADD/SUB Rm, Rn      Arithmetic
ADDI/SUBI #imm, Rn  Immediate arithmetic
INCR/DECR Rn        Increment/decrement

ANDI/XORI #imm, Rn  Logic immediate
AND/XOR Rm, Rn      Logic register

SLL/SLR Rn, 1/2     Shift left/right logical
SAR Rn, 1/2         Shift arithmetic right

B/BEQ/BNEQ addr     Branch unconditional/equal/not equal
BC/BNC addr         Branch carry set/clear
J addr              Jump
JSR Rn, addr        Jump subroutine (save PC in Rn)

PSHR/PULR Rn        Push/pull stack
```

### Cycle Counts (Performance Critical)
```
MVI:  8 cycles      MVII: 8 cycles
MVO:  9 cycles      ADD:  6 cycles
Branch: 7-9 cycles
```

### Memory Map
```
$0000-$003F   STIC registers (VBLANK only!)
$0040-$01EF   System RAM
$01F0-$01FF   Controller input
$0200-$035F   BACKTAB (screen, 240 words)
$0400-$04FF   GRAM (optional, 256 words)
$0500-$xxxx   Cartridge ROM
$D000-$DFFF   GROM (graphics ROM)
$F000-$FFFF   EXEC ROM
```

---

## STIC Graphics Chip

### MOB (Sprite) Registers

**8 MOBs total, 3 registers each:**
```
$0000-$0007: X positions
$0008-$000F: Y positions
$0010-$0017: Attributes (card + color)
```

**X Register:**
```
Bits 0-7:  X position (0-168 visible)
Bit 8:     Interaction (collision detect)
Bit 9:     Visibility
Bit 10:    Double width

Common: X_pos + $300 (interaction + visibility on)
```

**Y Register:**
```
Bits 0-6:  Y position (0-95 visible)
Bit 7:     Double height (16 lines)
Bits 8-9:  Scale (00=×0.5, 01=×1, 10=×2, 11=×4)
Bit 10:    X flip
Bit 11:    Y flip

Common: Y_pos + $200 (1× scale)
```

**Attribute Register:**
```
Bits 0-2:  Color (low 3 bits)
Bits 3-11: Card number
           0-255:   GROM
           256-319: GRAM
Bit 12:    Color (high bit, makes 4-bit color)
Bit 13:    Priority (0=foreground, 1=background)

Colors: 0-15
  0=Black, 1=Blue, 2=Red, 3=Tan, 4=DkGreen
  5=Green, 6=Yellow, 7=White, 8-15=repeat brighter
```

### BACKTAB (Screen Memory)

**Location:** $0200-$035F (20×12 = 240 words)

**Color Stack Mode (default):**
```
Bits 0-2:  Foreground color
Bits 3-11: Card number (0-511)
Bit 12:    Foreground color bit 3
Bit 13:    Advance color stack
```

**Position Calculation:**
```
screen_pos = row * 20 + col
  row: 0-11
  col: 0-19
```

### Collision Registers

**Location:** $0018-$001F (read after WAIT)
```
$0018: COL0 (MOB 0 collisions)
$0019: COL1
...
$001F: COL7

Bits 0-7: Hit MOBs 0-7
Bit 8:    Hit background pixel
Bit 9:    Hit border
```

### Display Control
```
$0020: Display enable/mode
  Bit 0: Enable
  Bit 1: 0=color stack, 1=fg/bg mode

$0021-$0024: Color stack values (0-15)
$0028: Horizontal delay (0-7 pixels)
$0029: Vertical delay (0-7 pixels)
$002C: Border color (0-15)
$0030: Border mask (bit 0=left, bit 1=top)
```

### Scrolling

**Display Size:**
- BACKTAB: 20×12 tiles = 160×96 pixels
- Visible: ~159×88-96 pixels (varies by TV overscan)

**Smooth Scrolling:**

Hardware scroll registers ($0028/$0029) offset display 0-7 pixels without changing BACKTAB. When crossing 8-pixel boundary, shift BACKTAB content and reset offset.

**Algorithm:**
```
1. Increment offset (0→1→2...→7)
2. Write to $0028 (horizontal) or $0029 (vertical)
3. At offset=8:
   - Reset offset to 0
   - Shift entire BACKTAB by 1 tile
   - Load new edge tiles from map
```

**MOB Correction (CRITICAL):**

Scroll registers affect BACKTAB ONLY. MOBs must be manually adjusted:

```asm
; MOB world position = 1000
; Scroll offset = 200
; Screen position = 1000 - 200 = 800
```

For each MOB, subtract scroll offset from world coordinates before writing to STIC.

### GRAM (Graphics RAM)

**Location:** $3000-$33FF
**Cards:** 256-319 (64 cards)

Each card = 8×8 pixels = 8 bytes (1 byte/row)

**Example:**
```
Card 256 at $3000-$3007:
  $3000: %00011000    XX
  $3001: %00100100   X  X
  $3002: %01000010  X    X
  $3003: %01111110  XXXXXX
  ...
```

**Loading Limit:** ~18 cards/frame (NTSC)

### Critical Timing

**VBLANK:** Only safe time to write STIC registers
**Duration:** ~1.3ms (20-25 scanlines)
**Frame:** 16.67ms @ 60Hz NTSC, 20ms @ 50Hz PAL

---

## PSG Sound Chip (AY-3-8914)

### Registers (via $01F0)

**Tone Generators:**
```
$00-$01: Channel A freq (12-bit)
$02-$03: Channel B freq
$04-$05: Channel C freq

Frequency = 3579545 / (32 × Hz)  [NTSC]

Examples:
  A4 (440Hz):  254
  C5 (523Hz):  214
  A5 (880Hz):  127
```

**Volume:**
```
$08: Channel A volume (0-15, or 16=envelope)
$09: Channel B volume
$0A: Channel C volume
```

**Mixer:**
```
$07: Enable bits (0=on, 1=off)
  Bits 0-2: Tone A/B/C
  Bits 3-5: Noise A/B/C

Common: $38 = tones on, noise off
```

**Noise:**
```
$06: Noise period (0-31)
```

**Envelope:**
```
$0B-$0C: Period (16-bit)
$0D: Shape (0-15)
  0:  \______ Decay
  11: /‾‾‾‾‾‾ Attack+hold
  14: /\/\/\/ Sawtooth
```

---

## GROM Character Map

**ASCII to GROM mapping:**
```
32-95:  Direct (space, !, ", #, ..., A-Z, etc)
97-122: Lowercase a-z (if present)

Common characters:
  32: (space)   65-90: A-Z
  48-57: 0-9    97-122: a-z
```

**Special Cards:**
```
0: Blank/space
1-31: Symbols (varies by GROM version)
128-255: Extended (card suits, box drawing, etc)
```

---

## Assembly Patterns

### MOB Setup
```asm
; Enable MOB 0
MVII #(X_POS + $300), R0    ; X + interact + visible
MVO  R0, $0000
MVII #(Y_POS + $200), R0    ; Y + 1x scale
MVO  R0, $0008
MVII #(CARD + COLOR), R0    ; Card and color
MVO  R0, $0010

; Disable MOB
CLRR R0
MVO  R0, $0000
MVO  R0, $0008
MVO  R0, $0010
```

### VBLANK Wait
```asm
@@wait:
  MVI  $0020, R0      ; Read display enable
  ANDI #1, R0         ; Check active
  BEQ  @@wait         ; Loop until VBLANK
  ; Safe to write STIC now
```

### Collision Check
```asm
; Check MOB 0 hit anything
MVI  $0018, R0        ; Read COL0
ANDI #$FF, R0         ; MOB collision bits
BEQ  @@no_hit

; Check specific MOB
ANDI #$02, R0         ; Bit 1 = MOB 1
BNEQ @@hit_mob1

; Check background
MVI  $0018, R0
ANDI #$100, R0        ; Bit 8 = background
BNEQ @@hit_bg
```

### Fast Multiply/Divide
```asm
; Multiply by power of 2
SLL  R0, 1            ; ×2
SLL  R0, 2            ; ×4

; Divide by power of 2
SLR  R0, 1            ; ÷2 unsigned
SAR  R0, 1            ; ÷2 signed

; Multiply by 3
ADD  R0, R0           ; ×2
ADD  R1, R0           ; +original = ×3
```

### Screen Position
```asm
; Calculate screen offset
; screen_pos = row * 20 + col

; Method 1: Multiply
MVII #20, R1
CALL MULT16           ; R0 = row × 20
ADD  R2, R0           ; + col

; Method 2: Shifts (20 = 16 + 4)
MOVR R0, R1
SLL  R0, 2            ; ×4
SLL  R1, 4            ; ×16
ADD  R1, R0           ; ×20
ADD  R2, R0           ; + col
```

### Controller Input
```asm
; Read left controller
MVI  $01FF, R0        ; Get controller
COMR R0               ; Complement
ANDI #$0F, R0         ; Mask disc bits

; Check direction
ANDI #$08, R0         ; Bit 3 = up
BNEQ @@up
ANDI #$04, R0         ; Bit 2 = left
BNEQ @@left
```

---

## Optimization Rules

**DO:**
- Use shifts for ×2, ×4, ×8, ÷2, ÷4, ÷8
- Keep hot values in registers
- Write STIC only during VBLANK
- Batch GRAM updates (max ~18/frame)
- Unroll small loops

**DON'T:**
- Write STIC outside VBLANK
- Use multiply/divide in tight loops
- Access memory unnecessarily
- Forget interaction bit ($300) for collisions
- Load >18 GRAM cards/frame

---

## Frame Budget (NTSC)

```
Total: 14,934 cycles (16.67ms)
VBLANK: ~1,000-1,500 cycles usable

Typical breakdown:
  Controller:    ~100 cycles
  Game logic:  ~5,000 cycles
  STIC updates:  ~500 cycles
  GRAM updates:  ~200 cycles/card
  Sound:         ~100 cycles
  Reserve:     ~3,000 cycles for peaks
```

---

## Common Pitfalls

1. **STIC writes outside VBLANK** → glitches
2. **Too many GRAM updates** → graphics flicker
3. **Missing interaction bit** → no collisions
4. **Wrong color bits** → bit 12 separate from 0-2
5. **Collision before WAIT** → stale data
6. **Stack overflow** → R6 grows downward
7. **16-bit immediate without SDBD** → truncated

---

## Quick Lookup Tables

### Powers of 2 (for shifts)
```
2:   SLL Rn, 1
4:   SLL Rn, 2
8:   SLL Rn, 2; SLL Rn, 1
16:  SLL Rn, 2; SLL Rn, 2
32:  SLL Rn, 2; SLL Rn, 2; SLL Rn, 1
```

### Common Colors
```
0: Black       4: Dark Green  8: Blue
1: Blue        5: Green       9: Red
2: Red         6: Yellow     10: Tan
3: Tan         7: White      11-15: Brighter variants
```

### Screen Corners
```
Top-left:     $0200 (pos 0)
Top-right:    $0213 (pos 19)
Bottom-left:  $034C (pos 220)
Bottom-right: $035F (pos 239)
Center:       $02A9 (pos 169, row 8 col 9)
```

---

**This reference documents publicly available Intellivision hardware behavior.**
**For complete specifications, see spatula-city.org/~im14u2c/intv/**

Keep this file in your assembly project root for quick reference.
