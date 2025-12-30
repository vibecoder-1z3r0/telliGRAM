# telliGRAM - User Workflows

## Overview

This document describes common user workflows and how they map to telliGRAM's features.

---

## Workflow 1: Creating Your First GRAM Card

**Scenario:** New user wants to create a player ship sprite

### Steps:

1. **Launch telliGRAM**
   ```
   Open app → Defaults to GRAM Cards mode
   ```

2. **Create New Card**
   ```
   Click [+ New Card] button
   → Opens Edit Mode with empty 8×8 grid
   → Card assigned to first available slot (e.g., Card #0)
   ```

3. **Draw Sprite**
   ```
   Select Pencil tool (P)
   Click pixels to draw ship shape:
     ..XXXX..
     .XXXXXX.
     XXXXXXXX
     XX.XX.XX
     X..XX..X
     ....XX..
     ...X..X.
     ...X..X.
   ```

4. **Preview with Colors**
   ```
   In Preview Panel:
   Select Foreground: 7 (White)
   Select Background: 0 (Black)
   → See ship preview in white on black
   ```

5. **Name Card**
   ```
   Double-click label area
   Enter: "player_ship"
   Press Enter
   ```

6. **Export Code**
   ```
   Click [Export...] button
   Select format: IntyBASIC
   ☑ Include DEFINE statement
   Click [Copy]
   → Code copied to clipboard
   ```

7. **Paste into IntyBASIC Project**
   ```
   IntyBASIC code:
   player_ship:
       BITMAP "..XXXX.."
       BITMAP ".XXXXXX."
       BITMAP "XXXXXXXX"
       BITMAP "XX.XX.XX"
       BITMAP "X..XX..X"
       BITMAP "....XX.."
       BITMAP "...X..X."
       BITMAP "...X..X."

   DEFINE 0, 1, player_ship
   WAIT
   ```

**Result:** ✅ First GRAM card created and ready to use!

---

## Workflow 2: Creating a Walk Animation

**Scenario:** Create a 4-frame walk cycle for the player

### Steps:

1. **Create Animation Frames (GRAM Cards)**
   ```
   GRAM Cards mode → Create 4 new cards:

   Card #8 (walk_1):  Card #9 (walk_2):  Card #10 (walk_3): Card #11 (walk_4):
     ..XXX...            ..XXX...            ..XXX...            ..XXX...
     .X...X..            .X...X..            .X...X..            .X...X..
     X.....X.            X.....X.            X.....X.            X.....X.
     X..X..X.            X..X..X.            X..X..X.            X..X..X.
     X.....X.            X.....X.            X.....X.            X.....X.
     .X...X..            .X...X..            .X...X..            .X...X..
     ..X.X...  (stance)  ...X.... (step)     ..X.X... (stance)   .X.....  (step)
     ...X....            ..X.X...            ...X....            ...X.X..
   ```

2. **Use Onion Skinning**
   ```
   While editing Card #9:
   ☑ Enable Onion Skin
   → See Card #8 ghosted in background
   → Adjust pixels for smooth motion

   Repeat for Cards #10 and #11
   ```

3. **Multi-Select Cards**
   ```
   Grid View:
   Click Card #8
   Shift+Click Card #11
   → Cards 8-11 selected
   ```

4. **Create Animation from Selection**
   ```
   Click [Create Animation...] button
   Enter name: "walk_right"
   → Switches to Animations mode
   → Timeline created with frames 8, 9, 10, 11
   ```

5. **Adjust Timing**
   ```
   Timeline shows:
   ┌───┬───┬───┬───┐
   │ 8 │ 9 │10 │11 │
   └─┬─┴─┬─┴─┬─┴─┬─┘
     4   4   4   4   ← Default 4 ticks each

   Click duration numbers to edit
   Change to: 6, 4, 6, 4 (longer on stance frames)
   ```

6. **Make It Loop Smoothly**
   ```
   Add reverse sequence for smooth cycle:
   ┌───┬───┬───┬───┬───┬───┐
   │ 8 │ 9 │10 │11 │10 │ 9 │
   └─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┘
     6   4   6   4   6   4

   Total: 30 ticks = 0.5 seconds @ 60Hz
   ```

7. **Test Animation**
   ```
   Click [▶️ Play]
   Enable [🔁 Loop]
   → Watch walk cycle at 60 FPS
   → Looks smooth!
   ```

8. **Export Animation Code**
   ```
   Click [Export Code...]
   Format: IntyBASIC
   ☑ Include timing data
   ☑ Include playback code
   Click [Copy]
   ```

9. **Use in Game**
   ```
   IntyBASIC code:
   walk_right_frames:
       DATA 256, 257, 258, 259, 258, 257
   walk_right_timing:
       DATA 6, 4, 6, 4, 6, 4

   ' In game loop:
   anim_timer = anim_timer + 1
   IF anim_timer >= walk_right_timing(anim_frame) THEN
       anim_timer = 0
       anim_frame = (anim_frame + 1) MOD 6
   END IF
   SPRITE 0, x + $300, y + $200, walk_right_frames(anim_frame) + 7
   ```

**Result:** ✅ Smooth walk animation ready for game!

---

## Workflow 3: Designing a Title Screen

**Scenario:** Create "SPACE QUEST" title screen using GROM and GRAM

### Steps:

1. **Plan Screen Layout**
   ```
   20×12 BACKTAB = 240 positions

   Layout:
   Row 0-1:  Empty (border space)
   Row 2-3:  "SPACE QUEST" title
   Row 4-7:  Custom GRAM logo/art
   Row 8-9:  "PRESS BUTTON" (GROM text)
   Row 10-11: Empty
   ```

2. **Check GROM for Text**
   ```
   Switch to [GROM Cards] mode
   Search for letters: S P A C E Q U E S T

   Found all in GROM:
   S = Card 51
   P = Card 48
   A = Card 33
   C = Card 35
   E = Card 37
   Q = Card 49
   U = Card 53
   T = Card 52

   ✅ No need to waste GRAM on text!
   ```

3. **Create Custom Logo (GRAM)**
   ```
   Switch to [GRAM Cards] mode
   Create 8 cards for custom logo graphic:

   Cards #0-7: Large "SPACE" logo design
   (Each 8×8 card is part of larger 32×16 logo)
   ```

4. **Switch to Screen Layout Mode**
   ```
   Click [Screen] tab
   → Shows 20×12 BACKTAB grid
   ```

5. **Place Title Text (GROM)**
   ```
   GROM palette → Expand "Common" → Letters

   Click 'S' (GROM 51)
   → Paint mode active
   Click screen at Row 2, Col 5
   → 'S' placed

   Continue for "SPACE QUEST"
   Row 2: S P A C E
   Row 3: Q U E S T

   All centered (start col ~7)
   ```

6. **Place Custom Logo (GRAM)**
   ```
   GRAM palette → Select Cards #0-7

   Place in 2×4 grid:
   Row 5:  Card #0 | Card #1 | Card #2 | Card #3
   Row 6:  Card #4 | Card #5 | Card #6 | Card #7

   → Forms complete logo
   ```

7. **Add Blinking "PRESS BUTTON"**
   ```
   Row 8-9, centered:
   GROM text: "PRESS BUTTON"

   (Animation handled in game code with color changes)
   ```

8. **Preview Screen**
   ```
   Zoom to 200% to see full layout
   Toggle grid off for clean view

   Screen looks great! ✅
   ```

9. **Export Screen Data**
   ```
   Click [Export BACKTAB Data...]
   Format: IntyBASIC SCREEN
   ☑ Include comments
   ☑ Include position labels

   Generated code:
   title_screen:
       ' Row 0 (empty)
       DATA 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
       ' Row 1 (empty)
       DATA 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
       ' Row 2 (SPACE)
       DATA 0,0,0,0,0,0,0,51,48,33,35,37,0,0,0,0,0,0,0,0
       ' Row 3 (QUEST)
       DATA 0,0,0,0,0,0,0,49,53,37,51,52,0,0,0,0,0,0,0,0
       ' Rows 4-5 (logo GRAM cards 256-263)
       ...

   Click [Copy]
   ```

10. **Use in IntyBASIC**
    ```
    ' Load GRAM cards first
    DEFINE 0, 8, logo_graphics
    WAIT

    ' Display screen
    CLS
    SCREEN title_screen
    ```

**Result:** ✅ Professional title screen using GROM + GRAM efficiently!

---

## Workflow 4: Optimizing GRAM Usage

**Scenario:** Running out of GRAM slots, need to optimize

### Steps:

1. **Check GRAM Usage**
   ```
   Status bar shows: "GRAM: 58/64 used"
   ⚠️ Warning: Only 6 slots left!
   ```

2. **Review All Cards**
   ```
   GRAM Cards mode → Grid view
   Look for:
   - Duplicate cards
   - Cards that match GROM
   - Unused cards
   ```

3. **Find GROM Duplicates**
   ```
   telliGRAM automatically detects:

   ⚠️ Card #23 is identical to GROM 33 ('A')
   ⚠️ Card #24 is identical to GROM 16 ('0')
   ⚠️ Card #25 is identical to GROM 0 (space)

   Suggestion: Use GROM instead!
   ```

4. **Replace with GROM References**
   ```
   For each duplicate:
   1. Note which screens/animations use it
   2. Switch to Screen Layout
   3. Find all instances of GRAM card
   4. Replace with GROM card
   5. Delete GRAM card

   GRAM: 58/64 → 55/64 ✅
   ```

5. **Merge Similar Cards**
   ```
   Cards #30 and #31 are 95% identical
   → Could use same card with flip_h flag

   Delete Card #31
   Update code to flip Card #30 instead

   GRAM: 55/64 → 54/64 ✅
   ```

6. **Remove Unused Cards**
   ```
   Search project:
   Cards #40-45 not used anywhere
   → Created for test, forgot to delete

   Select Cards #40-45
   Press Delete

   GRAM: 54/64 → 48/64 ✅
   ```

7. **Optimize Animations**
   ```
   Walk animations use cards:
   walk_right: 8, 9, 10, 11
   walk_left:  12, 13, 14, 15

   Optimization: Use same cards, flip horizontally!
   walk_left: 8(flip), 9(flip), 10(flip), 11(flip)

   Delete cards #12-15
   Update animation with flip_h=True

   GRAM: 48/64 → 44/64 ✅
   ```

8. **Final Check**
   ```
   GRAM: 44/64 used
   ✅ 20 slots free!
   ✅ All duplicates removed
   ✅ Using GROM where possible
   ✅ Animations optimized
   ```

**Result:** ✅ Freed 14 GRAM slots through optimization!

---

## Workflow 5: Importing Existing Sprite Sheet

**Scenario:** Have a sprite sheet PNG, want to import as GRAM cards

### Steps:

1. **Prepare Sprite Sheet**
   ```
   Image: player_sprites.png
   Size: 64×32 pixels
   Grid: 8 sprites in 8×8 tiles (8 columns × 4 rows)
   Format: 2-color PNG (black & white)
   ```

2. **Import Image**
   ```
   File → Import Image...
   Select: player_sprites.png

   telliGRAM detects:
   ✅ 8×8 grid found
   ✅ 32 sprites detected
   ✅ All sprites are 2-color ✓
   ```

3. **Import Dialog**
   ```
   ┌─────────────────────────────────┐
   │ Import Sprite Sheet             │
   ├─────────────────────────────────┤
   │ Detected: 32 sprites (8×8)      │
   │                                  │
   │ Import to GRAM slots:            │
   │ ● Start at slot #0               │
   │ ○ Start at slot #___             │
   │ ○ Replace specific slots...      │
   │                                  │
   │ Options:                         │
   │ ☑ Auto-name cards (sprite_0...)  │
   │ ☑ Detect animations              │
   │ ☑ Remove duplicates              │
   │                                  │
   │ Preview:                         │
   │ ┌─┬─┬─┬─┬─┬─┬─┬─┐              │
   │ │0│1│2│3│4│5│6│7│              │
   │ └─┴─┴─┴─┴─┴─┴─┴─┘              │
   │ ...                              │
   │                                  │
   │ [Import] [Cancel]                │
   └─────────────────────────────────┘
   ```

4. **Auto-Detect Animations**
   ```
   telliGRAM analyzes sprite sheet:

   Detected patterns:
   - Cards 0-3: Similar (walk cycle?)
   - Cards 4-7: Similar (run cycle?)
   - Cards 8-11: Similar (jump sequence?)

   Create animations automatically?
   ☑ walk_cycle (cards 0-3)
   ☑ run_cycle (cards 4-7)
   ☑ jump_sequence (cards 8-11)

   [Create Animations]
   ```

5. **Import Complete**
   ```
   ✅ Imported 32 GRAM cards
   ✅ Created 3 animations
   ✅ Auto-named all cards

   GRAM Cards mode shows all imported sprites
   Animations mode shows 3 ready-to-use animations
   ```

6. **Verify Import**
   ```
   Click through each card
   Check pixel accuracy
   Test animations with playback

   ✅ All sprites imported correctly!
   ```

7. **Export for Game**
   ```
   Export → All GRAM cards + Animations
   Format: Assembly (binary)

   Ready to use in game!
   ```

**Result:** ✅ Entire sprite sheet imported and ready to use!

---

## Workflow 6: Quick Prototyping

**Scenario:** Game jam - need sprites FAST!

### Speed Tips:

1. **Use Keyboard Shortcuts**
   ```
   Ctrl+N - New card
   P - Pencil (paint fast!)
   H/V - Flip horizontal/vertical
   Ctrl+D - Duplicate
   Ctrl+E - Export
   ```

2. **Copy-Paste-Modify**
   ```
   Create one enemy sprite
   Duplicate 3 times (Ctrl+D, Ctrl+D, Ctrl+D)
   Modify each slightly (different colors/details)
   → 4 enemy variants in 2 minutes!
   ```

3. **Use Symmetry**
   ```
   Draw half of sprite
   Duplicate → Flip H
   → Instant left/right variants!
   ```

4. **Start from GROM**
   ```
   Browse GROM cards
   Find close match
   Copy to GRAM
   Modify slightly
   → Faster than from scratch!
   ```

5. **Batch Export**
   ```
   Select all cards
   Export everything at once
   → Single .bas file with all graphics
   ```

**Result:** ✅ Complete sprite set in under 30 minutes!

---

## Workflow 7: Collaborative Development

**Scenario:** Working with a team, sharing assets

### Steps:

1. **Save Project File**
   ```
   File → Save Project
   Filename: space_game.telligram

   Contains:
   - All GRAM cards
   - All animations
   - Screen layouts
   - Project settings

   Format: JSON (version control friendly!)
   ```

2. **Share Project File**
   ```
   Commit to Git:
   git add assets/space_game.telligram
   git commit -m "Add player sprites and animations"
   git push
   ```

3. **Teammate Opens File**
   ```
   git pull
   Open telliGRAM
   File → Open Project
   Select: space_game.telligram

   ✅ All GRAM cards loaded
   ✅ All animations loaded
   ✅ Ready to edit!
   ```

4. **Export for Build**
   ```
   Export → All assets
   Format: IntyBASIC
   Output: game_graphics.bas

   Include in game repository:
   INCLUDE "game_graphics.bas"
   ```

5. **Merge Changes**
   ```
   .telligram is JSON:
   - Git can merge changes
   - Resolve conflicts if needed
   - Review diffs in pull requests
   ```

**Result:** ✅ Team can collaborate on graphics efficiently!

---

## Common Patterns

### Pattern 1: Character with Multiple States

```
Character needs:
- Idle (1 card)
- Walk (4 cards, animation)
- Jump (3 cards, animation)
- Hurt (2 cards, animation)

Total: 10 GRAM cards, 3 animations
```

### Pattern 2: Screen Transitions

```
Title Screen → GROM text + GRAM logo (8 cards)
Game Screen → GRAM sprites (20 cards) + GROM HUD text
Game Over → GROM text only (0 cards)

Total: 28 GRAM cards across all screens
```

### Pattern 3: Enemy Variants

```
Base enemy: 4 cards (animation)
Duplicate + modify colors → 3 variants
Use same animation frames
→ Efficient reuse!
```

---

**These workflows demonstrate telliGRAM's flexibility for various development scenarios!** 🚀
