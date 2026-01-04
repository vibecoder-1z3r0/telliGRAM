# Feature: STIC Figures - Complete screen layout designer with BACKTAB and MOBs

## Summary

Adds **STIC Figures**: a complete Intellivision screen layout designer with BACKTAB grid editing and MOB (Moving Object Block) support.

## What's New

### STIC Figures Tab
- Complete 20×12 BACKTAB grid editor with visual canvas (48px tiles at 6× scale)
- Dual display modes: **Color Stack** and **Foreground/Background**
- Real-time canvas rendering with proper color handling
- Project integration: figures saved with .tlgm project files (no separate files)

### MOB Support (8 MOBs per figure)
- **Position**: X (0-175), Y (0-111) in INTV world coordinates
- **Card selection**: GRAM cards only (256-319)
- **Color**: 16-color palette selection
- **Priority**: Front/Back rendering (behind/in front of BACKTAB foreground)
- **Size**: 8×8, 8×16, 16×8, 16×16
- **Flip**: Horizontal and vertical flip support
- Real-time rendering on canvas with proper layering

### UI Features
- Figure management: Dropdown + New/Rename/Delete/Import/Export buttons
- Card palette with GRAM/GROM tabs (GROM hidden when no --grom flag)
- BACKTAB properties panel with display mode switching
- MOB controls panel (8 MOBs, 2-line layout per MOB, scrollable)
- Hover info toggle: Shows card #, row, col on canvas (optional)
- Selected tile info with world coordinates

### Data Model
- `SticFigure` class with full serialization (to_dict/from_dict)
- Stores: BACKTAB tiles, MOBs, color stack, border settings, display mode
- Project integration: Multiple figures per project
- Default figure created for new projects

## Technical Implementation

### Rendering Pipeline
Correct layer order for MOB priority:
1. BACKTAB backgrounds
2. MOBs with priority=False (behind)
3. BACKTAB foregrounds
4. Grid/selection/hover
5. MOBs with priority=True (in front)

### Coordinate System
- INTV world coords: X (0-175), Y (0-111) includes border
- Canvas scaling: × 6 for display
- MOB rendering: `mob_x = (mob['x'] - 1) * 6` (corrected offset)
- Example: X=7, Y=8 aligns with card 0

### MOB Rendering
- Transparent background (only foreground pixels)
- Size scaling with proper pixel multiplication
- H/V flip support in bitmap rendering
- Color application with INTV palette

## Files Changed

### New Files
- `telligram/core/stic_figure.py` - Core data model
- Tests for STIC Figures in `tests/core/test_project.py`

### Modified Files
- `telligram/gui/widgets/stic_figures.py` - Main STIC Figures widget (~1500 lines)
- `telligram/core/project.py` - Added stic_figures list
- `telligram/gui/main_window.py` - Integration + updated descriptions
- `pyproject.toml` - Updated app description

## Bug Fixes Included

- ✅ First figure not loading on project open (explicit load)
- ✅ Canvas not clearing on new project (clear_all_tiles)
- ✅ Mode switching not working (missing signal connection)
- ✅ MOBs not rendering (added rendering pipeline)
- ✅ Priority flag not working (split rendering passes)
- ✅ X coordinate off by 1 INTV pixel (corrected offset)
- ✅ GROM tab showing without GROM (conditional display)
- ✅ BACKTAB canvas blank without GROM (always set card sources)

## Testing

All existing tests pass. New tests added for:
- STIC Figure serialization
- Multiple figures per project
- All 240 tiles preserved
- MOB data persistence

## Documentation Updates

- App description now: "GRAM Card Creator, Animator and BACKTAB/STIC Designer"
- Window title updated
- About dialog updated

## Next Steps (Future Work)

- MOB animation support (link to Animation objects)
- Additional MOB sizes (4×, 8× scaling)
- Collision detection visualization
- BACKTAB export to IntyBASIC/Assembly
- Undo/Redo support for STIC Figures

---

**Commits:** 12
**Lines Added:** ~2000
**Full feature implementation** for Phase 1 of STIC Figures
