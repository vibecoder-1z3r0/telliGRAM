# telliGRAM - UX/UI Design Specification

## Design Philosophy

**telliGRAM is a specialized creative tool for Intellivision developers.** The UI should be:

- **Focused** - Optimized for 8×8 pixel art creation
- **Intuitive** - Familiar to anyone who's used pixel art or animation tools
- **Efficient** - Minimize clicks, maximize productivity
- **Educational** - Guide users toward good Intellivision development practices

---

## Application Modes

telliGRAM has **4 primary modes**, accessed via tabs:

```
┌────────────────────────────────────────────────────────────┐
│ File  Edit  View  Tools  Help                              │
├────────────────────────────────────────────────────────────┤
│ [📦 GRAM Cards] [📚 GROM Cards] [🖥️ Screen] [🎬 Animations] │
├────────────────────────────────────────────────────────────┤
│                                                             │
│                  (Mode content here)                        │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Mode Navigation

- **Click tab** to switch modes
- **Keyboard shortcuts:**
  - `Ctrl+1` - GRAM Cards
  - `Ctrl+2` - GROM Cards
  - `Ctrl+3` - Screen Layout
  - `Ctrl+4` - Animations

---

## Mode 1: GRAM Cards (Primary Mode)

**Purpose:** Create and manage your 64 custom GRAM cards

### View: Grid View (Default)

```
┌─────────────────────────────────────────────────────────────┐
│  GRAM Cards (12/64 used)                     [Grid ▾] [⚙️]  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐         │
│  │  0  │  1  │  2  │  3  │  4  │  5  │  6  │  7  │         │
│  │ ▓▒░ │ ░▒▓ │ ⚡  │ ▓▓▓ │ ░░░ │     │     │     │         │
│  │ship │plyr │bull │expl │coin │empty│empty│empty│         │
│  ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤         │
│  │  8  │  9  │ 10  │ 11  │ 12  │ 13  │ 14  │ 15  │         │
│  │ ⚡  │ ⚡  │ ⚡  │ ⚡  │     │     │     │     │         │
│  │wlk1 │wlk2 │wlk3 │wlk4 │empty│empty│empty│empty│         │
│  └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘         │
│  ... (continues to card 63)                                 │
│                                                              │
│  Selection: 4 cards (8-11)                                  │
│  [+ New] [Delete] [Duplicate] [Export] [Create Animation]  │
└─────────────────────────────────────────────────────────────┘
```

#### Grid View Features

**Card Display:**
- **Thumbnail preview** (32×32 or 64×64 pixels, zoomed from 8×8)
- **Card number** (0-63) → Maps to GRAM 256-319
- **Label** (optional, user-defined)
- **Empty indicator** for unused slots
- **Animation icon** (⚡) if card is part of animation

**Visual States:**
- **Normal** - Default appearance
- **Hover** - Subtle highlight
- **Selected** - Blue border/background
- **Multi-selected** - Blue border on all selected
- **Empty** - Gray/dimmed

**Grid Size Options:**
```
[Grid Size ▾]
  ○ Small (4×4 preview)
  ● Medium (8×8 preview)  ← Default
  ○ Large (16×16 preview)
  ○ Extra Large (32×32 preview)
```

#### Selection Modes

**Single Select:**
- Click card → Select it
- Double-click card → Enter Edit Mode

**Multi-Select:**
- `Ctrl+Click` - Add/remove from selection
- `Shift+Click` - Select range (from last selected to clicked)
- `Ctrl+A` - Select all cards
- `Drag box` - Box selection (like file explorer)

**Multi-Select Visual:**
```
┌─────┬─────┬─────┬─────┐
│  8  │  9  │ 10  │ 11  │  ← All have blue border
│ ⚡  │ ⚡  │ ⚡  │ ⚡  │
│wlk1 │wlk2 │wlk3 │wlk4 │  ← Selected count shown below
└─────┴─────┴─────┴─────┘
```

#### Context Menu (Right-Click)

```
Card 5: "player_ship"
──────────────────────
  Edit
  Rename
  Duplicate
  ──────────────────
  Clear Card
  Delete Card
  ──────────────────
  Copy
  Paste
  ──────────────────
  Export to IntyBASIC...
  Export to Assembly...
  ──────────────────
  Add to Animation...
```

**Multi-Select Context Menu:**
```
4 cards selected
──────────────────────
  Delete All
  Clear All
  Duplicate All
  ──────────────────
  Export Selection...
  ──────────────────
  Create Animation from Selection
```

#### Bottom Action Bar

```
┌────────────────────────────────────────────────────────┐
│ [+ New Card] [✏️ Edit] [🗑️ Delete] [📋 Duplicate]      │
│ [💾 Export...] [🎬 Create Animation...]                │
└────────────────────────────────────────────────────────┘
```

**Button States:**
- Disabled when no selection
- Enabled when ≥1 card selected
- Contextual tooltips (hover to see what it does)

### View: Edit Mode (Individual Card)

**Enter Edit Mode:**
- Double-click card in grid
- Select card + press `Enter`
- Select card + click "Edit" button
- Create new card

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to Grid      Card #5 "player_ship"      [Save] [X] │
├──────────────────────┬──────────────────────────────────────┤
│                      │                                      │
│  Pixel Editor        │  Preview Panel                       │
│  ┌────────────────┐  │  ┌──────────────────────────┐       │
│  │ Large 8×8 grid │  │  │ Live preview with colors │       │
│  │ (Zoomed 400%)  │  │  │                          │       │
│  │                │  │  │      [Ship Preview]      │       │
│  │                │  │  │                          │       │
│  │  Click to      │  │  │    With selected colors  │       │
│  │  paint pixels  │  │  └──────────────────────────┘       │
│  │                │  │                                      │
│  └────────────────┘  │  Preview Colors:                    │
│                      │  Foreground: [7 White  ▾]           │
│  Tools:              │  Background: [0 Black  ▾]           │
│  ● Pencil            │                                      │
│  ○ Eraser            │  Export:                            │
│  ○ Fill              │  ┌────────────────────────┐         │
│  ○ Line              │  │ BITMAP "..XXXX.."     │         │
│  ○ Rectangle         │  │ BITMAP ".XXXXXX."     │         │
│                      │  │ BITMAP "XXXXXXXX"     │         │
│  ☑ Show Grid         │  │ ...                   │         │
│  ☑ Onion Skin        │  └────────────────────────┘         │
│                      │  [Copy] [Export...]                 │
│                      │                                      │
│  Transform:          │  Binary:                            │
│  [Flip H] [Flip V]   │  FF 7E 3C 18 99 DB FF FF           │
│  [Rotate 90°]        │                                      │
│  [Clear] [Invert]    │  Hex:                               │
│                      │  $FF $7E $3C $18                    │
└──────────────────────┴──────────────────────────────────────┘
```

#### Pixel Editor (8×8 Grid)

**Zoom Levels:**
```
[Zoom: 400% ▾]
  200% - Small
  400% - Medium (Default)
  800% - Large
  1600% - Extra Large
```

**Grid Display:**
- **Major grid** - 8×8 card boundary (thick lines)
- **Minor grid** - Individual pixels (thin lines)
- **Toggle** with `G` key or checkbox

**Drawing Tools:**

1. **Pencil** (`P`) - Draw individual pixels
   - Click = Set pixel
   - Click+drag = Paint multiple
   - Hold `Shift` = Constrain to line

2. **Eraser** (`E`) - Clear pixels
   - Click = Clear pixel
   - Click+drag = Erase multiple

3. **Fill** (`F`) - Flood fill
   - Click pixel = Fill connected region

4. **Line** (`L`) - Draw straight lines
   - Click start, click end

5. **Rectangle** (`R`) - Draw rectangles
   - Click corner, drag to opposite corner
   - Hold `Shift` = Square

**Keyboard Shortcuts (Edit Mode):**
```
P - Pencil tool
E - Eraser tool
F - Fill tool
L - Line tool
R - Rectangle tool
G - Toggle grid
O - Toggle onion skin
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+C - Copy card
Ctrl+V - Paste card
H - Flip horizontal
V - Flip vertical
Space - Invert colors
Delete - Clear card
```

#### Preview Panel

**Live Preview:**
- Shows card with selected Intellivision colors
- Updates in real-time as you draw
- Scalable (1× to 8× zoom)

**Color Selection:**
```
Foreground Color: [7 White        ▾]
  ├─ 0 Black
  ├─ 1 Blue
  ├─ 2 Red
  ├─ 3 Tan
  ├─ 4 Dark Green
  ├─ 5 Green
  ├─ 6 Yellow
  ├─ 7 White ✓
  └─ 8-15 (Pastel variants)

Background Color: [0 Black        ▾]
  └─ (Same palette)
```

**Note:** Colors are **preview only** - not saved with card data. GRAM cards are 1-bit (pixel on/off only). Colors are applied when used in BACKTAB or MOB.

#### Code Export Panel

**Live Code Generation:**
Shows IntyBASIC or Assembly code as you draw:

```
┌─────────────────────────┐
│ Format: [IntyBASIC ▾]  │
├─────────────────────────┤
│ player_ship:            │
│     BITMAP "..XXXX.."   │
│     BITMAP ".XXXXXX."   │
│     BITMAP "XXXXXXXX"   │
│     BITMAP "XX.XX.XX"   │
│     BITMAP "X..XX..X"   │
│     BITMAP "....XX.."   │
│     BITMAP "...X..X."   │
│     BITMAP "...X..X."   │
├─────────────────────────┤
│ [📋 Copy] [💾 Export]   │
└─────────────────────────┘
```

**Format Toggle:**
- IntyBASIC (BITMAP statements)
- Assembly Binary (DECLE %)
- Assembly Hex (DECLE $)

#### Onion Skinning

**What is it:** See previous/next frames while drawing (for animation)

**Enable:**
```
☑ Onion Skin
  Previous frame: [50% opacity ▾]
  Next frame:     [30% opacity ▾]
```

**Visual:**
```
┌────────────────┐
│ Ghost of prev  │  ← 50% transparent
│  frame shown   │
│   behind       │
│  current frame │
└────────────────┘
```

**Use Case:** Creating walk cycle animation
- Edit frame 2
- See frame 1 ghosted behind
- Adjust pixels to create smooth motion

---

## Mode 2: GROM Cards (Reference Browser)

**Purpose:** Browse built-in GROM character set (read-only reference)

```
┌─────────────────────────────────────────────────────────────┐
│  GROM Character Set (256 cards)                             │
├─────────────────────────────────────────────────────────────┤
│  Filter: [All ▾]  Category: [All ▾]  Search: [________]    │
│  ☑ ASCII (0-94)  ☑ Extended (95-255)                       │
├─────────────────────────────────────────────────────────────┤
│  ASCII Characters (Cards 0-94)                              │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐       │
│  │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│10│11│12│13│14│15│       │
│  │SP│ !│ "│ #│ $│ %│ &│ '│ (│ )│ *│ +│ ,│ -│ .│ /│       │
│  ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤       │
│  │16│17│18│19│20│21│22│23│24│25│26│27│28│29│30│31│       │
│  │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│ :│ ;│ <│ =│ >│ ?│       │
│  ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤       │
│  │32│33│34│35│36│37│38│39│40│41│42│43│44│45│46│47│       │
│  │ @│ A│ B│ C│ D│ E│ F│ G│ H│ I│ J│ K│ L│ M│ N│ O│       │
│  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘       │
│  ... (continues to card 255)                                │
│                                                              │
│  Selected: Card 33 (GROM)                                   │
│  ┌────────────────────────────────────────────────┐         │
│  │ ASCII: 65 ('A')                                │         │
│  │ Category: Uppercase Letter                     │         │
│  │ GROM Card: 33  (= ASCII 65 - 32)              │         │
│  │                                                 │         │
│  │ Preview (8×8):        Zoomed:                  │         │
│  │ ░░▓▓▓░░░             ┌──────────┐             │         │
│  │ ░▓░░░▓░░             │          │             │         │
│  │ ▓░░░░░▓░             │    A     │             │         │
│  │ ▓░░░░░▓░             │          │             │         │
│  │ ▓▓▓▓▓▓▓░             └──────────┘             │         │
│  │ ▓░░░░░▓░                                       │         │
│  │                                                 │         │
│  │ [📋 Copy Card #] [➕ Use in Screen]            │         │
│  │ [⚠️ DON'T RECREATE IN GRAM!]                   │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### GROM Browser Features

**Filters & Search:**

```
Filter: [All ▾]
  ├─ All (0-255)
  ├─ ASCII Only (0-94)
  ├─ Extended Only (95-255)
  └─ Custom Range...

Category: [All ▾]
  ├─ All
  ├─ Letters
  ├─ Numbers
  ├─ Symbols
  ├─ Space/Control
  └─ Extended Graphics

Search:
  - By card number: "33"
  - By ASCII character: "A"
  - By ASCII code: "65"
  - By description: "letter"
```

**Quick Reference Table:**

```
┌─────────────────────────────────┐
│ Quick ASCII Lookup              │
├─────────────────────────────────┤
│ Space:    GROM 0    ASCII 32   │
│ 0-9:      GROM 16-25            │
│ A-Z:      GROM 33-58            │
│ a-z:      GROM 65-90            │
│                                  │
│ Formula: GROM = ASCII - 32      │
└─────────────────────────────────┘
```

**Right-Click Context Menu:**

```
Card 33 ('A')
────────────────────
  Copy Card Number (33)
  Copy as GROM Reference
  Copy ASCII Character ('A')
  ────────────────────
  Use in Screen Layout
  Add to Favorites
  ────────────────────
  View Details
```

**"Don't Recreate" Warning:**

When user tries to create identical GRAM card:

```
┌─────────────────────────────────────────────┐
│ ⚠️  Duplicate GROM Card Detected            │
├─────────────────────────────────────────────┤
│ Your GRAM card #5 is identical to:         │
│   GROM Card 33 ('A')                       │
│                                             │
│ This wastes a precious GRAM slot!          │
│                                             │
│ Suggestion: Delete this GRAM card and use  │
│ GROM card 33 instead.                      │
│                                             │
│ [Delete GRAM Card] [Keep Anyway] [Compare] │
└─────────────────────────────────────────────┘
```

---

## Mode 3: Screen Layout (BACKTAB Editor)

**Purpose:** Layout 20×12 screen using GRAM and GROM cards

```
┌─────────────────────────────────────────────────────────────┐
│  Screen Layout                           [Mode: Color Stack▾]│
├──────────────────────┬──────────────────────────────────────┤
│ Card Palette         │  BACKTAB (20×12)                     │
│                      │  ┌───────────────────────────────┐   │
│ GRAM Cards (12/64)   │  │ S C O R E :   0 0 0 0         │   │
│ ┌──┬──┬──┬──┬──┬──┐ │  │                               │   │
│ │ 0│ 1│ 2│ 3│ 4│ 5│ │  │           ⚡                  │   │
│ │▓▒│░▒│⚡│▓▓│░░│  │ │  │                               │   │
│ └──┴──┴──┴──┴──┴──┘ │  │                               │   │
│ ...                  │  │                               │   │
│                      │  │          [GAME AREA]          │   │
│ GROM Cards           │  │                               │   │
│ [Expand ▾]           │  │                               │   │
│ ├─ Common            │  │                               │   │
│ │  A-Z, 0-9         │  │                               │   │
│ ├─ Favorites         │  │                               │   │
│ │  (empty)          │  │                               │   │
│ └─ Browse All...     │  │                               │   │
│                      │  │                               │   │
│ Tools:               │  └───────────────────────────────┘   │
│ ● Paint              │                                      │
│ ○ Fill               │  Position: Row 0, Col 5 (Pos #5)    │
│ ○ Erase              │  Card: GROM 37 ('E')                │
│                      │  Color: Foreground 7 (White)        │
│ [Clear Screen]       │                                      │
│ [Import...]          │  [Export BACKTAB Data...]           │
└──────────────────────┴──────────────────────────────────────┘
```

### Screen Layout Features

**BACKTAB Grid:**
- **20 columns × 12 rows** = 240 card positions
- **Pixel size:** 160×96 (though only ~159×96 visible on real hardware)
- **Zoom levels:** 100%, 200%, 400%
- **Grid overlay:** Toggle with `G`

**Card Palette (Left Panel):**

```
GRAM Cards (Collapsible)
├─ [Show thumbnails ▾]
│  Shows all used GRAM cards
│  Click to select, drag to screen
│
└─ [Hide] to save space

GROM Cards (Collapsible)
├─ Common Characters
│  ├─ A-Z
│  ├─ 0-9
│  └─ Symbols
├─ Favorites
│  (User can star favorite GROM cards)
└─ Browse All...
   Opens GROM browser in sidebar
```

**Placement Tools:**

1. **Paint** - Click to place selected card
   - Select card from palette
   - Click position to place
   - Click+drag to paint multiple

2. **Fill** - Flood fill region
   - Click position
   - Fills connected cards of same type

3. **Erase** - Remove cards
   - Click to clear position
   - Leaves empty/black

4. **Rectangle Select** - Select region
   - Drag to select area
   - Copy/paste/fill selected region

**Position Info:**
```
Position: Row 5, Col 10
Formula: Pos = Row × 20 + Col = 110
Memory: $0200 + 110 = $026E
Card: GRAM 256 (GRAM slot 0)
Color: Stack mode, FG=7
```

**Right-Click on Screen:**
```
Position (5, 10)
────────────────────
  Clear
  Copy
  Paste
  ────────────────────
  Change Card...
  Change Color...
  ────────────────────
  Fill Region
```

**Export Screen Data:**

```
┌─────────────────────────────────┐
│ Export BACKTAB Data             │
├─────────────────────────────────┤
│ Format:                         │
│ ● IntyBASIC SCREEN data         │
│ ○ Assembly DECLE array          │
│                                  │
│ Options:                         │
│ ☑ Include comments              │
│ ☑ Include position labels       │
│ ☑ Include color stack data      │
│                                  │
│ Preview:                         │
│ ┌─────────────────────────────┐ │
│ │ screen_data:                │ │
│ │   DATA 51,35,47,50,37,26,0  │ │
│ │   DATA 16,16,16,16,0,0,...  │ │
│ └─────────────────────────────┘ │
│                                  │
│ [Copy] [Save to File...]        │
└─────────────────────────────────┘
```

---

## Mode 4: Animations (Timeline Editor)

**Purpose:** Create animation sequences from GRAM cards

```
┌─────────────────────────────────────────────────────────────┐
│  Animations                                  [New Animation] │
├─────────────────────────────────────────────────────────────┤
│  Animation List          │  Timeline Editor                  │
│                          │                                   │
│  ● walk_right (4f, loop) │  walk_right                       │
│  ○ walk_left (4f, loop)  │  ┌────────────────────────────┐  │
│  ○ idle (2f, loop)       │  │Frame: 1  2  3  4  3  2  1  │  │
│  ○ jump (3f, once)       │  │      ┌─┬─┬─┬─┬─┬─┬─┐      │  │
│                          │  │      │⚡│⚡│⚡│⚡│⚡│⚡│⚡│      │  │
│  [+ New]                 │  │      │8│9│A│B│A│9│8│      │  │
│  [Delete]                │  │      └┬┴┬┴┬┴┬┴┬┴┬┴┬┘      │  │
│  [Duplicate]             │  │       4 4 4 4 4 4 4       │  │
│                          │  │      (Duration in ticks)   │  │
│                          │  └────────────────────────────┘  │
│  Total GRAM used: 16/64  │                                   │
│                          │  ▶━━━━━━━━━━━━━━━━━━━━━━━━ 60Hz │
│                          │  Frame 3/7  Tick 12/28           │
│                          │                                   │
│                          │  [▶️ Play] [⏸️ Pause] [⏹️ Stop]   │
│                          │  [🔁 Loop] [⏮️] [⏭️]              │
│                          │                                   │
│                          │  Preview:                         │
│                          │  ┌──────────────────┐            │
│                          │  │   [Animation     │            │
│                          │  │    playing at    │            │
│                          │  │    60 FPS]       │            │
│                          │  └──────────────────┘            │
│                          │                                   │
│                          │  [Export Code...]                │
└─────────────────────────┴───────────────────────────────────┘
```

### Animation Timeline Features

**Frame Management:**
- **Add frame:** Click [+] or drag GRAM card to timeline
- **Remove frame:** Select frame, press Delete
- **Reorder:** Drag frames to reorder
- **Duration:** Click number to edit (in ticks @ 60Hz)
- **Copy frame:** Ctrl+C, Ctrl+V

**Playback Controls:**
```
▶️ Play - Start animation
⏸️ Pause - Pause at current frame
⏹️ Stop - Stop and reset to frame 0
⏮️ Previous Frame
⏭️ Next Frame
🔁 Loop - Toggle loop mode
```

**Frame Rate Options:**
```
[60 Hz ▾] NTSC
  ├─ 60 Hz (NTSC) ✓
  └─ 50 Hz (PAL)
```

**Timeline Visual:**
```
┌───┬───┬───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │ 3 │ 2 │ 1 │  ← Frame numbers
│▓▒░│░▒▓│▓▓▓│░░░│▓▓▓│░▒▓│▓▒░│  ← Thumbnails
└─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┘
  4   4   4   4   4   4   4      ← Duration (ticks)
  └─────────▲─────────┘
         Current
```

**Animation Properties Panel:**

```
┌────────────────────────────────┐
│ Animation: walk_right          │
├────────────────────────────────┤
│ Frames: 7                      │
│ Duration: 28 ticks (0.467s)    │
│ FPS: 60 Hz (NTSC)              │
│                                 │
│ Playback:                       │
│ ● Loop                          │
│ ○ One-shot                      │
│ ○ Ping-pong                     │
│                                 │
│ GRAM Cards Used: 4 (8-11)      │
│                                 │
│ [Rename...] [Delete]            │
└────────────────────────────────┘
```

**Export Animation Code:**

```
┌─────────────────────────────────────┐
│ Export Animation: walk_right        │
├─────────────────────────────────────┤
│ Format:                             │
│ ● IntyBASIC (DATA arrays)           │
│ ○ Assembly (DECLE arrays)           │
│                                      │
│ Include:                             │
│ ☑ Frame data                        │
│ ☑ Timing data                       │
│ ☑ Playback code template            │
│ ☑ Comments                           │
│                                      │
│ Preview:                             │
│ ┌─────────────────────────────────┐ │
│ │ walk_right_frames:              │ │
│ │   DATA 256,257,258,259,258,257  │ │
│ │ walk_right_timing:              │ │
│ │   DATA 4,4,4,4,4,4              │ │
│ └─────────────────────────────────┘ │
│                                      │
│ [Copy] [Save to File...]            │
└─────────────────────────────────────┘
```

---

## Color System Design

### Understanding GRAM Colors

**Key Concept:** GRAM cards are **1-bit** (black & white pixels only). Colors are applied separately when the card is used.

```
┌─────────────────────────────────────────────────┐
│ GRAM Card (in memory)   →   Used in Game       │
├─────────────────────────────────────────────────┤
│ 1-bit data:             │   With color:         │
│ ░░▓▓░░                  │   🟦🟦⬜⬜🟦🟦          │
│ ░▓▓▓▓░                  │   🟦⬜⬜⬜⬜🟦          │
│ ▓▓▓▓▓▓                  │   ⬜⬜⬜⬜⬜⬜          │
│                         │                       │
│ (Pixel on/off only)     │   (FG=Blue, BG=Black) │
└─────────────────────────────────────────────────┘
```

### Color Preview in telliGRAM

**Purpose:** Help visualize how card will look with different colors

**Implementation:**

```
┌────────────────────────────────┐
│ Preview Colors (Visualization) │
├────────────────────────────────┤
│ Foreground: [7 White      ▾]  │
│ Background: [0 Black      ▾]  │
│                                 │
│ ⚠️ Colors NOT saved in card!   │
│ Used for preview only.          │
│                                 │
│ Colors are set when card is     │
│ used in BACKTAB or MOB.         │
└────────────────────────────────┘
```

**Intellivision Color Palette:**

```
Primary (0-7):               Pastel (8-15):
┌───┬───┬───┬───┐           ┌───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │           │ 8 │ 9 │10 │11 │
│███│███│███│███│           │███│███│███│███│
│Blk│Blu│Red│Tan│           │Blu│Red│Tan│Grn│
├───┼───┼───┼───┤           ├───┼───┼───┼───┤
│ 4 │ 5 │ 6 │ 7 │           │12 │13 │14 │15 │
│███│███│███│███│           │███│███│███│███│
│DkG│Grn│Yel│Wht│           │Red│Yel│Yel│Wht│
└───┴───┴───┴───┘           └───┴───┴───┴───┘
```

---

## Keyboard Shortcuts

### Global (All Modes)

```
Ctrl+N      New project
Ctrl+O      Open project
Ctrl+S      Save project
Ctrl+Shift+S Save project as...
Ctrl+Q      Quit

Ctrl+Z      Undo
Ctrl+Y      Redo
Ctrl+C      Copy
Ctrl+V      Paste
Ctrl+X      Cut
Delete      Delete selection

Ctrl+1      GRAM Cards mode
Ctrl+2      GROM Cards mode
Ctrl+3      Screen Layout mode
Ctrl+4      Animations mode

F1          Help
F11         Fullscreen
```

### GRAM Cards Mode

```
Enter       Edit selected card
Space       Quick preview
N           New card
D           Duplicate selected
Delete      Delete selected
Ctrl+A      Select all cards
Ctrl+E      Export selected
```

### Edit Mode (Pixel Editor)

```
P           Pencil tool
E           Eraser tool
F           Fill tool
L           Line tool
R           Rectangle tool

G           Toggle grid
O           Toggle onion skin
H           Flip horizontal
V           Flip vertical

Ctrl+I      Invert pixels
Ctrl+Shift+C Clear card

Esc         Exit edit mode
```

### Screen Layout Mode

```
1           Paint tool
2           Fill tool
3           Erase tool
4           Select tool

G           Toggle grid
Z           Zoom in
X           Zoom out

Arrow keys  Move cursor
Space+Click Paint selected card
```

### Animation Mode

```
Space       Play/pause
Home        First frame
End         Last frame
Left        Previous frame
Right       Next frame

+           Add frame
Delete      Remove frame
```

---

## Status Bar

**Bottom of window, always visible:**

```
┌─────────────────────────────────────────────────────────────┐
│ Ready │ GRAM: 12/64 used │ Mode: Grid View │ Zoom: 400%    │
└─────────────────────────────────────────────────────────────┘
```

**Status Messages:**
- Operation feedback ("Card saved", "Exported to clipboard")
- Warning messages ("GRAM limit reached!", "Duplicate GROM detected")
- Progress indicators ("Saving project...", "Exporting...")

---

## Dialogs

### New Project Dialog

```
┌──────────────────────────────────┐
│ New Project                      │
├──────────────────────────────────┤
│ Project Name:                    │
│ [My Game_____________]           │
│                                   │
│ Author:                          │
│ [Your Name___________]           │
│                                   │
│ Target System:                   │
│ ● NTSC (60 Hz)                   │
│ ○ PAL (50 Hz)                    │
│                                   │
│ [Create] [Cancel]                │
└──────────────────────────────────┘
```

### Export Dialog

```
┌──────────────────────────────────────────┐
│ Export Options                           │
├──────────────────────────────────────────┤
│ Export:                                  │
│ ☑ GRAM card definitions                 │
│ ☑ Animations                             │
│ ☑ Screen layout (BACKTAB)               │
│                                           │
│ Format:                                   │
│ ● IntyBASIC                              │
│ ○ Assembly (binary)                      │
│ ○ Assembly (hexadecimal)                 │
│                                           │
│ Options:                                  │
│ ☑ Include comments                       │
│ ☑ Include DEFINE statements              │
│ ☑ Include helper code                    │
│ ☑ Visual documentation                   │
│                                           │
│ Output:                                   │
│ ● Copy to clipboard                      │
│ ○ Save to file                           │
│                                           │
│ [Export] [Cancel]                        │
└──────────────────────────────────────────┘
```

### Preferences Dialog

```
┌──────────────────────────────────────────┐
│ Preferences                              │
├──────────────────────────────────────────┤
│ [General] [Editor] [Export] [Advanced]  │
│                                           │
│ Editor:                                   │
│                                           │
│ Default zoom: [400% ▾]                   │
│ Grid color: [#808080]                    │
│ ☑ Show grid by default                  │
│ ☑ Auto-save every 5 minutes              │
│                                           │
│ Pixel editor:                             │
│ ☑ Show pixel coordinates on hover       │
│ ☑ Confirm before clearing card          │
│ Onion skin opacity: [50% ═════○════]    │
│                                           │
│ Export:                                   │
│ Default format: [IntyBASIC ▾]            │
│ ☑ Always include comments                │
│ Label prefix: [gfx_______]               │
│                                           │
│ [OK] [Cancel] [Apply]                    │
└──────────────────────────────────────────┘
```

---

## Visual Design Guidelines

### Color Scheme

**Light Theme (Default):**
- Background: #F5F5F5 (Light gray)
- Cards: #FFFFFF (White)
- Grid: #CCCCCC (Medium gray)
- Selection: #0078D4 (Blue)
- Text: #000000 (Black)

**Dark Theme:**
- Background: #1E1E1E (Dark gray)
- Cards: #252526 (Slightly lighter)
- Grid: #3E3E42 (Medium gray)
- Selection: #0078D4 (Blue)
- Text: #FFFFFF (White)

### Typography

```
Headings: Segoe UI, 14pt, Bold
Body: Segoe UI, 10pt, Regular
Code: Consolas, 10pt, Regular
Labels: Segoe UI, 9pt, Regular
```

### Spacing

```
Window padding: 8px
Panel padding: 12px
Button padding: 6px 12px
Grid gap: 4px
Section spacing: 16px
```

---

## Accessibility

- **Keyboard navigation** - Full app usable without mouse
- **Screen reader** - Labels on all interactive elements
- **High contrast** - Support high contrast themes
- **Tooltips** - Helpful tooltips everywhere
- **Undo/Redo** - Forgiving UI, easy to fix mistakes

---

**This UX specification provides the foundation for implementing telliGRAM's user interface with PySide6!** 🎨
