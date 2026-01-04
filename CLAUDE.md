# Claude Code Context - telliGRAM

This document contains important context for Claude Code to pick up development work.

## Recent Major Feature: STIC Figures (Phase 1)

### Overview
STIC Figures is a complete Intellivision screen layout designer that allows users to create full-screen compositions including:
- 20×12 BACKTAB grid (240 tiles of 8×8 pixel cards)
- 8 MOBs (Moving Object Blocks) with full configuration
- Border settings and color management
- Dual display modes (Color Stack / Foreground-Background)

### Architecture

#### Core Data Model (`telligram/core/stic_figure.py`)

**SticFigure class:**
```python
class SticFigure:
    name: str                    # Figure name
    mode: str                    # "color_stack" or "fg_bg"
    border_visible: bool         # Border display toggle
    border_color: int            # 0-15
    show_left_border: bool       # Left border (8px)
    show_top_border: bool        # Top border (8px)
    color_stack: List[int]       # [0-3] color indices
    _backtab: List[Dict]         # 240 tiles (20×12 grid)
    mobs: List[Dict]             # 8 MOBs
```

**BACKTAB Tile Structure:**
```python
{
    "row": int,              # 0-11
    "col": int,              # 0-19
    "card": int,             # 0-319 (card number)
    "fg_color": int,         # 0-15 (foreground color)
    "bg_color": int,         # 0-15 (FG/BG mode only)
    "advance_stack": bool    # Color Stack mode only
}
```

**MOB Structure:**
```python
{
    "visible": bool,         # Show/hide MOB
    "card": int,             # 256-319 (GRAM only)
    "x": int,                # 0-175 (INTV world coords)
    "y": int,                # 0-111 (INTV world coords)
    "color": int,            # 0-15 (foreground color)
    "priority": bool,        # False=behind, True=in front
    "size": int,             # 0=8×8, 1=8×16, 2=16×8, 3=16×16
    "h_flip": bool,          # Horizontal flip
    "v_flip": bool           # Vertical flip
}
```

**Serialization:**
- `to_dict()`: Exports to JSON-serializable dict (stored in .tlgm project files)
- `from_dict(data)`: Reconstructs from dict

#### UI Widget (`telligram/gui/widgets/stic_figures.py`)

**Main Components:**

1. **Left Panel - Card Palette (~500 lines)**
   - `CardPaletteWidget`: Tabbed interface for GRAM/GROM cards
   - GROM tab conditionally shown (only if GROM data loaded)
   - Clickable card thumbnails with labels
   - Selected card highlighting

2. **Center Panel - BACKTAB Canvas (~600 lines)**
   - `BacktabCanvas`: 20×12 grid renderer at 6× scale (48px tiles)
   - 8px border (48px at scale) on all sides
   - Display modes: Color Stack (simulates hardware) / FG-BG (direct colors)
   - Mouse interaction: click to select, Ctrl+click to paint
   - Hover info display (optional, toggleable)
   - Figure management controls below canvas

3. **Right Panel - Properties (~700 lines)**
   - Display settings (grid, border, hover info toggles)
   - Display mode selection (Color Stack / FG-BG)
   - Selected tile info with world coordinates
   - Card/color properties
   - Color Stack editor (4 slots)
   - **MOB Controls** (8 MOBs, scrollable)

**MOB UI Layout (per MOB):**
```
Row 1: [✓] 0: [Card▾] X[###] Y[###]
Row 2:     C:[■7▾] [✓]F/B S:[8×8▾] [✓]H [✓]V
```

### Coordinate Systems

**INTV World Coordinates:**
- Screen: 176×112 pixels (8px border + 160×96 playfield + 8px border)
- X range: 0-175 (left to right, includes borders)
- Y range: 0-111 (top to bottom, includes borders)
- Card 0 position: X=8, Y=8 (top-left playfield card after border)
- Screen center: X=88, Y=56

**Canvas Coordinates:**
- Scale factor: 6× (INTV pixel → 6 canvas pixels)
- Total size: 1056×672 canvas pixels
- Border: 48 canvas pixels (8 INTV × 6)

**MOB Rendering Formula:**
```python
# CRITICAL: X has -1 offset correction for proper alignment
mob_x = (mob['x'] - 1) * 6  # X=7, Y=8 aligns with card 0
mob_y = mob['y'] * 6
```

### Rendering Pipeline

**Critical Layer Order (for MOB priority):**
```python
1. BACKTAB backgrounds (all tiles)
2. MOBs with priority=False  ← Behind foreground
3. BACKTAB foregrounds (all tiles)
4. Grid lines
5. Selection highlight
6. Hover info overlay
7. MOBs with priority=True   ← In front of foreground
```

**Implementation:**
- Split rendering into background/foreground passes
- `_draw_mobs(painter, priority)` called twice
- Color Stack mode: Simulates hardware stack advancement
- FG-BG mode: Direct color application

**MOB Rendering (`_draw_mob_card`):**
- Transparent background (only draw foreground pixels)
- Size scaling: Multiply pixel dimensions by width_mult/height_mult
- Flip: Invert pixel coordinates before rendering
- Handles all 4 size modes

### Key Implementation Details

#### Critical Fixes Applied:
1. **First figure loading**: Explicitly call `_load_figure()` even when dropdown index=0
2. **Canvas clearing**: Call `clear_all_tiles()` before loading new figure
3. **Mode switching**: Connect both radio button signals to `_on_mode_changed`
4. **MOB rendering**: Render in two passes based on priority flag
5. **X coordinate**: Apply -1 offset for proper alignment
6. **GROM-less operation**: Always call `set_card_sources()` even when grom_data=None
7. **GROM tab visibility**: Conditionally add/remove tab in `set_grom_data()`

#### Signal/Slot Patterns:
```python
# Dropdown changes
self.figure_combo.currentIndexChanged.connect(self._on_figure_selected)

# Mode switching (both radios must connect!)
self.color_stack_radio.toggled.connect(self._on_mode_changed)
self.fg_bg_radio.toggled.connect(self._on_mode_changed)

# MOB controls (all 8 MOBs × 9 controls)
for mob_idx in range(8):
    controls['visible'].toggled.connect(lambda checked, idx=mob_idx: ...)
    controls['card'].currentIndexChanged.connect(lambda card_idx, idx=mob_idx: ...)
    # ... etc for all 9 controls
```

#### Data Synchronization:
```python
# When MOB control changes:
1. Update self.current_figure.mobs[idx][property]
2. Update self.canvas.mobs[idx][property]
3. Call self.canvas.update() to repaint

# When loading figure:
1. Load into self.current_figure
2. Copy to self.canvas.mobs
3. Load into UI controls (with blockSignals)
```

### Project Integration

**Project class (`telligram/core/project.py`):**
```python
class Project:
    stic_figures: List[SticFigure]  # Added

    def add_stic_figure(figure: SticFigure)
    def get_stic_figure(index: int) -> SticFigure
```

**Default initialization:**
```python
# main_window.py: New projects get default figure
default_figure = SticFigure(name="Figure 1")
self.project.add_stic_figure(default_figure)
```

**Serialization:**
- Figures stored in project .tlgm file as JSON
- `"stic_figures": [figure.to_dict(), ...]`
- All 240 tiles + 8 MOBs + settings preserved

### Known Issues / TODOs

**Phase 2 (Future):**
- [ ] MOB animation support (link to Animation objects)
- [ ] Additional MOB sizes (4×, 8× width/height scaling)
- [ ] Undo/Redo for STIC Figures (commands created but not integrated)
- [ ] BACKTAB export to IntyBASIC/Assembly
- [ ] Collision detection visualization
- [ ] Import/Export functionality for figures (currently placeholders)

**Current Limitations:**
- MOBs can only use GRAM cards (256-319), not GROM
- Size dropdown limited to 4 modes (8×8, 8×16, 16×8, 16×16)
- No visual MOB selection/dragging on canvas (properties panel only)

### File Locations

**Core:**
- `telligram/core/stic_figure.py` - Data model (~240 lines)
- `telligram/core/project.py` - Project integration

**GUI:**
- `telligram/gui/widgets/stic_figures.py` - Main widget (~1540 lines)
- `telligram/gui/main_window.py` - Tab integration

**Tests:**
- `tests/core/test_project.py` - STIC Figure serialization tests (8 new tests)

### Testing

**Run tests:**
```bash
python3 -m pytest tests/core/test_project.py -v -k stic
```

**Key test coverage:**
- Figure serialization (to_dict/from_dict)
- Multiple figures per project
- All 240 tiles preserved
- MOB data persistence
- Border/color stack settings

### Color Stack Mode Details

**How it works (simulates INTV hardware):**
1. Color stack has 4 slots (indices 0-3, each holds a color 0-15)
2. Stack position starts at 0
3. For each BACKTAB tile (row by row, left to right):
   - Background color = color_stack[position % 4]
   - If tile.advance_stack: position += 1
4. Next tile uses new position

**UI Implementation:**
- 4 color dropdowns for stack slots
- Per-tile "Advance Color Stack" checkbox
- Canvas renders by simulating stack advancement

### Debugging Tips

**Common issues:**
1. **Tiles not showing**: Check `set_card_sources()` called with gram_data
2. **MOBs not rendering**: Check `visible=True` and `self.canvas.mobs` populated
3. **Wrong colors**: Verify display mode matches figure.mode
4. **Coordinates off**: Remember X offset: `(x - 1) * 6`
5. **Mode switch broken**: Both radio buttons must connect to signal

**Useful debug points:**
- `_load_figure()`: Figure → canvas/UI synchronization
- `_draw_mobs()`: MOB rendering with priority filtering
- `_on_mob_*_changed()`: MOB property updates

### Code Style Notes

- Use `blockSignals(True/False)` when programmatically updating controls
- Always update both `current_figure` and `canvas` data
- Call `canvas.update()` after any visual change
- Use lambdas with default args for signal connections: `lambda x, idx=i: ...`

---

**Last Updated:** 2026-01-04
**Feature Status:** Phase 1 Complete, Ready for Merge
**Next Phase:** MOB Animations + Additional Sizes
