# Intellivision Assembly GRAM Card Format

## Overview

Intellivision assembly programs use the **as1600** assembler for the CP1610 processor. GRAM cards are defined using the `DECLE` directive (DECLaration of Elements), which outputs 10-bit words to memory.

## Syntax

### Basic Card Definition

```asm
label_name:
    DECLE %11111111    ; Row 0 (binary)
    DECLE %10000001    ; Row 1
    DECLE %10000001    ; Row 2
    DECLE %10000001    ; Row 3
    DECLE %10000001    ; Row 4
    DECLE %10000001    ; Row 5
    DECLE %10000001    ; Row 6
    DECLE %11111111    ; Row 7
```

### Number Format Options

Assembly supports multiple numeric formats:

#### Binary (Recommended for Graphics)
```asm
ship_gfx:
    DECLE %00011000    ; Row 0:    XX
    DECLE %00111100    ; Row 1:   XXXX
    DECLE %01111110    ; Row 2:  XXXXXX
    DECLE %11011011    ; Row 3: XX XX XX
    DECLE %11111111    ; Row 4: XXXXXXXX
    DECLE %01111110    ; Row 5:  XXXXXX
    DECLE %00111100    ; Row 6:   XXXX
    DECLE %00011000    ; Row 7:    XX
```

#### Hexadecimal
```asm
ship_gfx:
    DECLE $18    ; Row 0:    XX
    DECLE $3C    ; Row 1:   XXXX
    DECLE $7E    ; Row 2:  XXXXXX
    DECLE $DB    ; Row 3: XX XX XX
    DECLE $FF    ; Row 4: XXXXXXXX
    DECLE $7E    ; Row 5:  XXXXXX
    DECLE $3C    ; Row 6:   XXXX
    DECLE $18    ; Row 7:    XX
```

#### Decimal (Not Recommended)
```asm
ship_gfx:
    DECLE 24     ; Row 0
    DECLE 60     ; Row 1
    DECLE 126    ; Row 2
    DECLE 219    ; Row 3
    DECLE 255    ; Row 4
    DECLE 126    ; Row 5
    DECLE 60     ; Row 6
    DECLE 24     ; Row 7
```

### Multiple Cards

```asm
; Define multiple cards sequentially
player_sprites:
    ; Card 1 - Player facing right
    DECLE %00111000
    DECLE %01000100
    DECLE %10000010
    DECLE %10010010
    DECLE %10000010
    DECLE %01000100
    DECLE %00111000
    DECLE %00000000

    ; Card 2 - Player facing left
    DECLE %00011100
    DECLE %00100010
    DECLE %01000001
    DECLE %01001001
    DECLE %01000001
    DECLE %00100010
    DECLE %00011100
    DECLE %00000000
```

## DECLE Directive Details

### What is DECLE?

**DECLE** = "Declaration of Elements" (rhymes with "heckle")
- Originally meant a 10-bit "byte" (Intellivision word size)
- as1600 expanded it to mean "words that are the width of the ROM"
- Outputs one or more words of data to the program

### Syntax
```asm
DECLE value1, value2, value3    ; Multiple values on one line
DECLE value1                     ; Single value
```

### Related Directives

- **`BIDECLE`**: 16-bit value (two DECLEs)
- **`ROMW`**: Set ROM word width (default 10 bits)
- **`ORG`**: Set origin address

## Memory Locations

### GRAM Address Space
```asm
; GRAM is located at $3000-$33FF
; 64 cards × 8 bytes = 512 bytes total

; Card 256 (GRAM slot 0): $3000-$3007
; Card 257 (GRAM slot 1): $3008-$300F
; Card 258 (GRAM slot 2): $3010-$3017
; ...
; Card 319 (GRAM slot 63): $33F8-$33FF
```

### Defining Graphics in ROM

Graphics data is typically stored in ROM and copied to GRAM at runtime:

```asm
        ORG     $5000           ; ROM location

; Define graphics data in ROM
ship_gfx:
        DECLE   %00011000
        DECLE   %00111100
        DECLE   %01111110
        DECLE   %11011011
        DECLE   %11111111
        DECLE   %01111110
        DECLE   %00111100
        DECLE   %00011000

; Later: Copy to GRAM
        MVII    #ship_gfx, R4   ; Source address
        MVII    #$3000, R5      ; Destination (GRAM card 256)
        MVII    #8, R1          ; Count (8 bytes)
@@loop: MVI@    R4, R0          ; Read byte
        MVO@    R0, R5          ; Write to GRAM
        DECR    R1              ; Decrement counter
        BNEQ    @@loop          ; Loop until done
```

## Using GRAM Cards

### In BACKTAB (Background)

```asm
; Display GRAM card 256 at screen position (row 5, col 10)
; Screen address = $0200 + (row × 20 + col)
; = $0200 + (5 × 20 + 10) = $0200 + 110 = $026E

        MVII    #$1100, R0      ; Card 256 ($100) + color stack mode ($1000)
        MVO     R0, $026E       ; Write to BACKTAB
```

### In MOBs (Sprites)

```asm
; Set MOB 0 to display GRAM card 256 with color 3 (tan)
; MOB attribute = (card << 3) | color
; But for readability, IntyBASIC and macros use card + color

        MVII    #$100, R0       ; Card 256
        ADDI    #3, R0          ; + color 3
        MVO     R0, $0010       ; MOB 0 attribute register

; Or using bit shifting
        MVII    #256, R0        ; Card number
        SWAP    R0              ; Shift to bits 3-11
        SLL     R0, 2
        SLL     R0, 1
        ADDI    #3, R0          ; Add color
        MVO     R0, $0010
```

## Macro Libraries

The SDK-1600 includes macro libraries that simplify GRAM operations:

### stic.mac Macros (Typical)

```asm
        INCLUDE "stic.mac"

; GRAMSLICE macro (example - actual syntax may vary)
        GRAMSLICE %11111111, %10000001, %10000001, %10000001

; GRAMCARD macro (example)
        GRAMCARD %11111111, %10000001, %10000001, %10000001, \
                 %10000001, %10000001, %10000001, %11111111
```

**Note:** Actual macro syntax varies by SDK version. Check `stic.mac` file for exact definitions.

## Advanced Techniques

### Compressed Graphics

Using assembler expressions to reduce duplication:

```asm
; Vertical symmetry
ship_gfx:
        DECLE   %00011000    ; Row 0
        DECLE   %00111100    ; Row 1
        DECLE   %01111110    ; Row 2
        DECLE   %11111111    ; Row 3
        DECLE   %11111111    ; Row 3 (repeat)
        DECLE   %01111110    ; Row 2 (repeat)
        DECLE   %00111100    ; Row 1 (repeat)
        DECLE   %00011000    ; Row 0 (repeat)

; Can use labels to avoid repeating values
ship_gfx:
ship_r0: DECLE  %00011000
ship_r1: DECLE  %00111100
ship_r2: DECLE  %01111110
ship_r3: DECLE  %11111111
        DECLE   ship_r3      ; Reference same value
        DECLE   ship_r2
        DECLE   ship_r1
        DECLE   ship_r0
```

### Including External Files

```asm
        INCLUDE "graphics.asm"    ; Include graphics definitions
```

This allows graphics to be maintained in separate files.

## Comments and Documentation

### Inline Comments
```asm
ship_gfx:
        DECLE   %00011000    ; Row 0:    XX
        DECLE   %00111100    ; Row 1:   XXXX
        DECLE   %01111110    ; Row 2:  XXXXXX
        DECLE   %11011011    ; Row 3: XX XX XX
        DECLE   %11111111    ; Row 4: XXXXXXXX
        DECLE   %01111110    ; Row 5:  XXXXXX
        DECLE   %00111100    ; Row 6:   XXXX
        DECLE   %00011000    ; Row 7:    XX
```

### Visual Block Comments
```asm
;; ======================================================================
;; PLAYER SHIP GRAPHICS
;; ======================================================================
;;    XX
;;   XXXX
;;  XXXXXX
;; XX XX XX
;; XXXXXXXX
;;  XXXXXX
;;   XXXX
;;    XX
;; ======================================================================
ship_gfx:
        DECLE   %00011000
        DECLE   %00111100
        DECLE   %01111110
        DECLE   %11011011
        DECLE   %11111111
        DECLE   %01111110
        DECLE   %00111100
        DECLE   %00011000
```

## Best Practices

### 1. Use Binary for Graphics Data
```asm
; Good - visually clear
DECLE %11111111
DECLE %10000001

; Less clear - requires mental conversion
DECLE $FF
DECLE $81
```

### 2. Align Comments for Readability
```asm
sprite_data:
        DECLE   %00111000    ; Row 0
        DECLE   %01000100    ; Row 1
        DECLE   %10000010    ; Row 2
        DECLE   %10010010    ; Row 3
        DECLE   %10000010    ; Row 4
        DECLE   %01000100    ; Row 5
        DECLE   %00111000    ; Row 6
        DECLE   %00000000    ; Row 7
```

### 3. Group Related Graphics
```asm
;; Player animation frames
player_walk:
player_walk_1:
        DECLE   %00111000, %01000100, %10000010, %10010010
        DECLE   %10000010, %01000100, %00101000, %00010000

player_walk_2:
        DECLE   %00111000, %01000100, %10000010, %10010010
        DECLE   %10000010, %01000100, %00010000, %00101000
```

### 4. Use Meaningful Labels
```asm
; Good
player_ship_small:
enemy_tank_left:
explosion_frame_1:

; Bad
gfx1:
sprite2:
data:
```

## telliGRAM Output Format

For telliGRAM assembly output, we'll use:

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

**Format choices:**
- Binary format (`%`) for clarity
- Aligned comments with row numbers
- Consistent indentation (8 spaces after DECLE)
- Optional visual representation in block comment above

### Alternative: Hexadecimal Output

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

telliGRAM should support both binary and hexadecimal output formats.

## Complete Example

```asm
;; ======================================================================
;; Game Graphics Data
;; ======================================================================
        ORG     $5000

;; ----------------------------------------------------------------------
;; Player Ship
;;    XX
;;   XXXX
;;  XXXXXX
;; XXXXXXXX
;; XX XX XX
;; X  XX  X
;;    XX
;;   X  X
;; ----------------------------------------------------------------------
player_ship:
        DECLE   %00011000    ; Row 0
        DECLE   %00111100    ; Row 1
        DECLE   %01111110    ; Row 2
        DECLE   %11111111    ; Row 3
        DECLE   %11011011    ; Row 4
        DECLE   %10011001    ; Row 5
        DECLE   %00011000    ; Row 6
        DECLE   %00100100    ; Row 7

;; ----------------------------------------------------------------------
;; Enemy Tank
;; ----------------------------------------------------------------------
enemy_tank:
        DECLE   %00111100    ; Row 0
        DECLE   %01111110    ; Row 1
        DECLE   %11111111    ; Row 2
        DECLE   %11111111    ; Row 3
        DECLE   %11111111    ; Row 4
        DECLE   %01111110    ; Row 5
        DECLE   %00111100    ; Row 6
        DECLE   %00011000    ; Row 7

;; ======================================================================
;; Initialization - Copy graphics to GRAM
;; ======================================================================
init_graphics:
        ; Copy player ship to GRAM card 256
        MVII    #player_ship, R4
        MVII    #$3000, R5
        MVII    #8, R1
@@copy: MVI@    R4, R0
        MVO@    R0, R5
        DECR    R1
        BNEQ    @@copy

        JR      R5              ; Return
```

## References

- [DECLE - Intellivision Wiki](https://wiki.intellivision.us/index.php/DECLE)
- [Assembly Syntax Overview - Intellivision Wiki](http://wiki.intellivision.us/index.php?title=Assembly_Syntax_Overview)
- as1600 Assembler Documentation (SDK-1600)
- [Graphics RAM - Intellivision Wiki](http://wiki.intellivision.us/index.php/Graphics_RAM)
