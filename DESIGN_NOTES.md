# telliGRAM Design Notes & Future Features

This document tracks design decisions, planned features, and implementation notes for telliGRAM.

## Current Implementation Status

### ✅ Completed Features

- **GRAM Card Editor** (8×8 pixel editing, 64 slots)
  - Click-to-paint interface
  - Grid visualization
  - Flip horizontal/vertical
  - Clear card
  - Undo/redo support

- **Project Management**
  - JSON-based project files
  - Save/load projects
  - Unsaved changes indicator (*)
  - Full undo/redo stack

- **Animation System (Basic)**
  - Multiple named animations per project
  - Frame-based timeline (single layer)
  - Frame duration controls
  - Drag-and-drop frame reordering
  - Timeline playback (play/pause/stop/rewind)
  - Variable playback speed (1-60 fps)
  - Loop mode
  - Animation preview
  - Full undo/redo for all operations

- **Export Functionality**
  - Export to IntyBASIC (visual + data format)
  - Export to MBCC (C compiler)
  - Export to Assembly
  - Animation export (all formats)

## Planned Features

### 🎨 Phase 1: Color & GROM Support (Foundation)

**Priority:** High
**Complexity:** Low-Medium
**Impact:** High

#### 1.1 Intellivision Color Palette

**Goal:** Add color support for visual preview and export metadata

**Design:**
- 16-color Intellivision palette (STIC standard colors)
- Each GRAM card has optional display color
- Color stored in project file, exported as metadata/constants
- Color picker widget in UI

**Technical Notes:**
- Colors are purely cosmetic in editor (GRAM cards are 1-bit)
- Real color is applied at runtime via MOB color registers
- Need to define standard Intellivision color constants

**UI Changes:**
- Color picker button/swatch for each card
- Card grid shows cards in their assigned colors
- Pixel editor shows current card's color
- Animation preview respects card colors

#### 1.2 GROM (Graphics ROM) Support

**Goal:** Browse and use built-in Intellivision graphics

**Design Options:**

**Option A: Read-Only Browser**
- Separate GROM viewer panel
- Display all GROM cards (read-only)
- Can select GROM cards for use in animations
- Timeline distinguishes GROM vs GRAM cards (icon/badge)

**Option B: Unified View**
- Card grid shows GROM + GRAM together
- GROM cards grayed out/marked read-only
- Can't edit GROM, but can use in animations

**Option C: Import to GRAM**
- Browse GROM cards
- "Copy to GRAM" button to duplicate a GROM card
- Edit the copy in GRAM slot

**Decision:** TBD - need to evaluate UX trade-offs

**Technical Notes:**
- GROM addresses are ROM locations
- Need GROM card definitions (bitmap data)
- Export must distinguish GROM vs GRAM references

### 🎬 Phase 2: Multi-Layer Timeline (Advanced Animation)

**Priority:** High
**Complexity:** High
**Impact:** Very High

#### 2.1 Multi-Track Timeline

**Goal:** Support layered sprite composition like video editing software

**Design:**
```
Timeline Structure:
┌─────────────────────────────────────────────────┐
│ Layer 2 (Top):    [Card 5,5f][Card 6,5f][...]   │
│ Layer 1 (Mid):    [Card 9,7f][Card 10,8f]       │
│ Layer 0 (Bottom): [Card 12, 20 frames........]  │
└─────────────────────────────────────────────────┘
         0f    5f    10f   15f   20f
```

**Key Requirements:**

1. **Multiple Layer Tracks**
   - Each animation has N layers (default 1 for backward compatibility)
   - Layers rendered bottom-to-top (layer 0 = background, top layer = foreground)
   - Add/remove/reorder layers

2. **Timeline Clips**
   - Each clip = GRAM/GROM card + color + duration
   - Clips positioned on timeline at specific frame offsets
   - Clips can be different lengths on each layer
   - Drag clips horizontally to reposition
   - Resize clip duration by dragging edges
   - Drag clips between layers

3. **Playback & Compositing**
   - Global playhead scrubs through timeline
   - At each frame, sample all active layers
   - Composite layers bottom-to-top with transparency
   - Preview shows final composited result

4. **Export Implications**
   - Each layer = one MOB (Moving Object)
   - Need to track which MOBs are active at each frame
   - Export must include MOB positioning code
   - Different layers may need different colors

**Technical Challenges:**
- Data model: How to represent clips on timeline?
- UI: Multi-track timeline widget (like Premiere/After Effects)
- Compositing: Render layered sprites with transparency
- MOB limits: Intellivision has 8 MOBs max - need validation
- Export complexity: Generate code for multi-MOB positioning

**Data Model Ideas:**

```python
class Animation:
    name: str
    fps: int
    loop: bool
    layers: List[Layer]  # New: multiple layers

class Layer:
    name: str  # e.g., "Body", "Overlay", "Effects"
    clips: List[Clip]

class Clip:
    card_ref: CardReference  # GRAM slot or GROM address
    color: int  # Intellivision color index (0-15)
    start_frame: int  # Timeline position
    duration: int  # Length in frames
    # Future: x/y offset for positioning
```

**UI Components Needed:**
- Multi-track timeline widget
- Layer panel (add/remove/reorder)
- Clip manipulation (drag, resize, split)
- Timeline ruler with frame markers
- Compositing preview

### 🔲 Phase 3: Multi-Card Sprite Editing

**Priority:** Medium
**Complexity:** High
**Impact:** Medium

#### 3.1 Large Sprite Canvas

**Goal:** Edit 2×2, 2×1, 1×2, etc. sprites as unified canvases

**Design Options:**

**Option A: Linked Card Groups**
- Define "sprite groups" linking multiple GRAM cards
- Special editor mode showing all cards arranged spatially
- Edits to canvas update individual cards
- Grid overlay shows card boundaries

**Option B: Multi-Card Canvas Mode**
- Toggle between "single card" and "multi-card" modes
- Select layout (2×2, 2×1, etc.)
- Automatically allocates consecutive GRAM slots
- Paint seamlessly across card boundaries

**Use Cases:**
- Large characters (16×16 = 2×2 cards)
- Wide objects (16×8 = 2×1 cards)
- Tall objects (8×16 = 1×2 cards, but STIC supports this natively)

**Technical Notes:**
- STIC supports 8×8 and 8×16 MOBs natively (single/double height)
- For 2-wide sprites, need to position 2 MOBs side-by-side
- Multi-card sprites consume more GRAM slots
- Animation timeline should support sprite groups

**Challenges:**
- Slot allocation: Which GRAM slots to use?
- Timeline integration: How to represent in animation?
- Export: Code generation for multi-MOB positioning

## Technical Considerations

### Intellivision STIC Constraints

- **GRAM Cards:** 64 slots (addresses 256-319), 8×8 pixels, 1-bit per pixel
- **GROM Cards:** Built-in ROM graphics, read-only
- **MOBs:** 8 Moving Objects max, each can be 8×8 or 8×16
- **Colors:** 16-color palette, one color per MOB
- **Frame Rate:** 60 Hz (60 fps maximum)

### Intellivision Color Palette (STIC)

Standard 16-color palette (RGB hex values from jzIntv emulator):

| Index | Name          | Hex RGB   | RGB Values      | Description                |
|-------|---------------|-----------|-----------------|----------------------------|
| 0     | Black         | `#0C0005` | (12, 0, 5)      | Background color           |
| 1     | Blue          | `#002DFF` | (0, 45, 255)    | Primary blue               |
| 2     | Red           | `#FF3E00` | (255, 62, 0)    | Primary red                |
| 3     | Tan           | `#C9CFAB` | (201, 207, 171) | Beige/tan                  |
| 4     | Dark Green    | `#386B3F` | (56, 107, 63)   | Forest green               |
| 5     | Green         | `#00A756` | (0, 167, 86)    | Bright green               |
| 6     | Yellow        | `#FAEB27` | (250, 235, 39)  | Bright yellow              |
| 7     | White         | `#FCFFFF` | (252, 255, 255) | White/lightest             |
| 8     | Gray          | `#A7A8A8` | (167, 168, 168) | Medium gray                |
| 9     | Cyan          | `#5ACBFF` | (90, 203, 255)  | Light blue/cyan            |
| 10    | Orange        | `#FFA048` | (255, 160, 72)  | Orange                     |
| 11    | Brown         | `#BD8438` | (189, 132, 56)  | Brown/dark orange          |
| 12    | Pink          | `#FF3276` | (255, 50, 118)  | Magenta/pink               |
| 13    | Light Blue    | `#5EB5FF` | (94, 181, 255)  | Sky blue                   |
| 14    | Yellow-Green  | `#C3D959` | (195, 217, 89)  | Lime/yellow-green          |
| 15    | Purple        | `#C45CEC` | (196, 92, 236)  | Purple/violet              |

**Notes:**
- Colors 0-7 are the primary palette
- Colors 8-15 are secondary/extended colors
- Color 0 (Black) is typically used for transparency in sprites
- Actual display colors varied by TV/monitor in the 1980s
- These values are from jzIntv, the most accurate emulator

### Data Model Evolution

**Current:**
```python
Animation {
    frames: List[{card_slot: int, duration: int}]
}
```

**Future (with layers):**
```python
Animation {
    layers: List[Layer]
}

Layer {
    clips: List[Clip]
}

Clip {
    card_ref: CardReference,
    color: int,
    start_frame: int,
    duration: int
}
```

### Backward Compatibility

- Phase 1 (color): Easy - add optional color field, default to white
- Phase 2 (layers): Convert old animations to single-layer format
- Need migration code for loading old project files

### Export Code Generation

**Current:** Simple frame sequence

**Future (with layers):**
- Track active MOBs at each frame
- Generate MOB positioning code
- Handle MOB color changes
- Optimize for MOB reuse (don't redraw if unchanged)

## Open Questions

1. **GROM Implementation:** Which option (A/B/C) for GROM support?
2. **Layer Limits:** Should we enforce MOB limits (8 max) in UI?
3. **Timeline UI:** Build custom or use existing library?
4. **Color Export:** How to export color data? Constants? Data tables?
5. **Multi-card Sprites:** Is this needed if we have layers?
6. **MOB Positioning:** Should timeline include X/Y position editing?
7. **Collision Detection:** Export collision masks for sprites?

## Implementation Phases

### Phase 1: Foundation (Color + GROM)
**Estimated Effort:** 2-3 weeks

1. Define Intellivision color palette constants
2. Add color field to GRAMCard class
3. Implement color picker UI
4. Update all preview widgets to respect colors
5. Implement GROM card loader
6. Add GROM browser UI
7. Update animation timeline to support GROM references
8. Update export code to include color metadata

### Phase 2: Multi-Layer Timeline
**Estimated Effort:** 6-8 weeks

1. Design and implement new data model (Layer, Clip)
2. Build multi-track timeline widget
3. Implement layer panel
4. Add clip manipulation (drag, resize)
5. Implement compositing preview
6. Update playback engine
7. Migration code for old projects
8. Update export code for multi-MOB support
9. Extensive testing

### Phase 3: Multi-Card Sprites (Optional)
**Estimated Effort:** 3-4 weeks

1. Design sprite group system
2. Implement multi-card canvas editor
3. Integration with timeline
4. Export code generation

## Notes from Design Discussions

### 2026-01-01: Multi-Layer Timeline Discussion

**Key Insight:** Users need independent timelines per layer, not just stacked frames.

Example scenario:
- Layer 2 (character body): Changes every 5 frames
- Layer 1 (effects overlay): Changes every 7-8 frames
- Layer 0 (background): Static for 20 frames

This is more like video compositing than simple frame layers.

**Implication:** Need full timeline editor with:
- Clip positioning
- Variable clip lengths
- Per-layer timing independence
- Timeline scrubbing
- Composited preview

**Reference:** Think Premiere/After Effects for sprite animation

---

**Last Updated:** 2026-01-01
