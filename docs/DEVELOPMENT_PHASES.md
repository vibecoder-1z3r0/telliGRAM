# telliGRAM - Development Phases

## Overview

Strict TDD development in 4 major phases, each broken into testable iterations.

---

## Phase 1: Core Data Models (Weeks 1-2)

**Goal:** Bulletproof, 100% tested foundation - NO GUI YET

### Iteration 1.1: GramCard Class (2-3 days)
- ✅ **TDD Cycle:**
  1. Write `test_card.py` tests
  2. Implement `GramCard` class
  3. Achieve 100% coverage

- **Features:**
  - Create empty 8×8 card
  - Create from byte array
  - Get/set individual pixels
  - Export to bytes, binary strings, hex strings
  - Flip horizontal/vertical
  - Clear/fill operations

### Iteration 1.2: GROM Database (2-3 days)
- ✅ **TDD Cycle:**
  1. Write `test_grom.py` tests
  2. Implement `GromDatabase` class
  3. Load GROM character data

- **Features:**
  - Get card by number (0-255)
  - Get card by ASCII character
  - ASCII ↔ GROM conversion
  - String to card numbers
  - Card metadata (description, category)
  - Search/filter capabilities

### Iteration 1.3: Animation System (3-4 days)
- ✅ **TDD Cycle:**
  1. Write `test_animation.py` tests
  2. Implement `Animation` and `Frame` classes
  3. Test edge cases (looping, ping-pong)

- **Features:**
  - Frame with card ID, duration, flips
  - Animation with frame list
  - Add/remove/reorder frames
  - Calculate total duration
  - Get frame at specific tick
  - Loop/ping-pong modes

### Iteration 1.4: Screen Layout (2-3 days)
- ✅ **TDD Cycle:**
  1. Write `test_screen.py` tests
  2. Implement `BacktabScreen` class
  3. Test 20×12 grid operations

- **Features:**
  - 20×12 BACKTAB grid
  - Set/get card at position
  - Position ↔ (row, col) conversion
  - Fill region with card
  - Import/export screen data
  - Color stack mode settings

### Iteration 1.5: Project Model (2 days)
- ✅ **TDD Cycle:**
  1. Write `test_project.py` tests
  2. Implement `Project` class
  3. Test save/load with JSON

- **Features:**
  - Project metadata (name, author, version)
  - Collection of GRAM cards
  - Collection of animations
  - Screen layout
  - Save to JSON
  - Load from JSON
  - Validation

---

## Phase 2: Code Generators (Week 3)

**Goal:** Generate perfect IntyBASIC and Assembly code

### Iteration 2.1: IntyBASIC Generator (2-3 days)
- ✅ **TDD Cycle:**
  1. Write `test_intybasic.py` with expected outputs
  2. Implement `IntyBasicGenerator`
  3. Test all formatting options

- **Features:**
  - Generate BITMAP statements
  - Custom pixel characters (X/., #/., etc.)
  - Multiple cards
  - Animation DATA arrays
  - DEFINE statements
  - Playback code templates
  - Comments and documentation

### Iteration 2.2: Assembly Generator (Binary) (2-3 days)
- ✅ **TDD Cycle:**
  1. Write `test_assembly.py` tests
  2. Implement `AssemblyGenerator` (binary mode)
  3. Test formatting and alignment

- **Features:**
  - Generate DECLE statements (binary)
  - Visual comments
  - Block comment headers
  - Multiple cards
  - Animation arrays
  - GRAM copy routines
  - Proper indentation

### Iteration 2.3: Assembly Generator (Hex) (1-2 days)
- ✅ **TDD Cycle:**
  1. Extend `test_assembly.py`
  2. Add hexadecimal mode
  3. Test both formats

- **Features:**
  - DECLE statements (hexadecimal)
  - Inline visual comments
  - Format selection

### Iteration 2.4: Screen Data Generator (2 days)
- ✅ **TDD Cycle:**
  1. Write `test_screen_data.py`
  2. Implement BACKTAB data generator
  3. Test both languages

- **Features:**
  - Generate BACKTAB initialization
  - IntyBASIC SCREEN data
  - Assembly ORG and DECLE
  - Color stack mode data
  - Position comments

---

## Phase 3: GUI Foundation (Week 4)

**Goal:** Interactive editors with real-time preview

### Iteration 3.1: Main Window (1 day)
- ✅ **Integration Test:**
  1. Write `test_main_window.py`
  2. Create basic window layout
  3. Test menu actions

- **Features:**
  - Menu bar (File, Edit, View, Tools, Help)
  - Toolbar
  - Status bar
  - Dock widget layout
  - File operations (New, Open, Save)

### Iteration 3.2: Pixel Editor Widget (2-3 days)
- ✅ **Integration Test:**
  1. Write `test_pixel_editor.py`
  2. Implement 8×8 grid widget
  3. Test mouse interactions

- **Features:**
  - 8×8 clickable grid
  - Zoom levels
  - Mouse paint/erase
  - Keyboard shortcuts
  - Undo/redo
  - Current/preview colors
  - Grid overlay toggle

### Iteration 3.3: Card List Widget (1-2 days)
- ✅ **Integration Test:**
  1. Write `test_card_list.py`
  2. Implement scrollable card list
  3. Test selection

- **Features:**
  - List of 64 GRAM slots
  - Thumbnail previews
  - Add/delete cards
  - Rename cards
  - Selection
  - Drag to reorder

### Iteration 3.4: GROM Picker Widget (1-2 days)
- ✅ **Integration Test:**
  1. Write `test_grom_picker.py`
  2. Display GROM characters
  3. Test search/filter

- **Features:**
  - Grid of GROM characters
  - Character info on hover
  - Search by ASCII
  - Category filter
  - Click to insert into screen

---

## Phase 4: Advanced Features (Weeks 5-6)

### Iteration 4.1: Animation Timeline (3-4 days)
- ✅ **Integration Test:**
  1. Write `test_animation_timeline.py`
  2. Implement timeline widget
  3. Test playback

- **Features:**
  - Horizontal timeline
  - Frame thumbnails
  - Add/remove/reorder frames
  - Frame duration editing
  - Playback controls
  - Real-time preview @ 60Hz
  - Loop/ping-pong toggle
  - Onion skinning

### Iteration 4.2: Screen Layout Editor (3-4 days)
- ✅ **Integration Test:**
  1. Write `test_screen_layout.py`
  2. Implement 20×12 grid widget
  3. Test drag & drop

- **Features:**
  - 20×12 BACKTAB grid
  - Drag GROM/GRAM cards
  - Click to paint
  - Fill tool
  - Position info
  - Color preview
  - Export selection

### Iteration 4.3: Export Dialog (2 days)
- ✅ **Integration Test:**
  1. Write `test_export_dialog.py`
  2. Implement export options
  3. Test code generation

- **Features:**
  - Format selection (IntyBASIC/Assembly)
  - Options (comments, DEFINE, etc.)
  - Preview generated code
  - Copy to clipboard
  - Save to file
  - Batch export

### Iteration 4.4: Project Management (2 days)
- ✅ **Integration Test:**
  1. Write `test_project_management.py`
  2. Implement save/load
  3. Test file format

- **Features:**
  - Save project (.telligram JSON)
  - Load project
  - Auto-save
  - Recent files
  - Project properties dialog

### Iteration 4.5: Polish & UX (3-4 days)
- ✅ **Integration Test:**
  1. User testing
  2. Fix usability issues
  3. Performance optimization

- **Features:**
  - Keyboard shortcuts
  - Tooltips everywhere
  - Help documentation
  - Tutorial/welcome screen
  - Preferences dialog
  - Theme support
  - Icon set

---

## Testing Strategy

### Unit Tests (Core)
```bash
# Run during development
pytest tests/core/ -v

# Fast, 100% coverage required
pytest tests/core/ --cov=src/telligram/core --cov-report=term-missing
```

### Unit Tests (Codegen)
```bash
# Test code generation
pytest tests/codegen/ -v

# 95%+ coverage required
pytest tests/codegen/ --cov=src/telligram/codegen
```

### Integration Tests (GUI)
```bash
# Slower, test widget interactions
pytest tests/gui/ -v

# 70%+ coverage target
pytest tests/gui/ --cov=src/telligram/gui
```

### End-to-End Tests
```bash
# Full workflow tests
pytest tests/integration/ -v

# Create card → animate → export → verify output
```

---

## Daily Workflow

### Morning (TDD Cycle)
1. **Pick next iteration**
2. **Write tests first** (Red phase)
   ```bash
   pytest tests/core/test_card.py::TestNewFeature -v
   # All tests should FAIL ❌
   ```
3. **Commit failing tests**
   ```bash
   git add tests/
   git commit -m "Add tests for GramCard.flip_horizontal"
   ```

### Afternoon (Implementation)
4. **Implement minimal code** (Green phase)
   ```bash
   # Edit src/telligram/core/card.py
   pytest tests/core/test_card.py::TestNewFeature -v
   # All tests should PASS ✅
   ```
5. **Refactor** (Blue phase)
   ```bash
   # Improve code, keep tests green
   pytest tests/core/test_card.py -v
   # Still PASS ✅
   ```
6. **Commit implementation**
   ```bash
   git add src/ tests/
   git commit -m "Implement GramCard.flip_horizontal"
   ```

### Evening (Review)
7. **Check coverage**
   ```bash
   pytest --cov=src/telligram --cov-report=html
   open htmlcov/index.html
   ```
8. **Update progress**
   ```bash
   # Update this file with ✅
   ```

---

## Coverage Requirements

| Phase | Module | Min Coverage |
|-------|--------|--------------|
| 1 | core/* | 100% |
| 2 | codegen/* | 95% |
| 3 | gui/widgets/* | 70% |
| 4 | gui/* | 70% |

---

## Estimated Timeline

| Phase | Duration | Completion |
|-------|----------|------------|
| Phase 1: Core Models | 2 weeks | Week 2 |
| Phase 2: Code Generators | 1 week | Week 3 |
| Phase 3: GUI Foundation | 1 week | Week 4 |
| Phase 4: Advanced Features | 2 weeks | Week 6 |
| **Total** | **6 weeks** | |

---

## Success Metrics

- ✅ All core modules at 100% test coverage
- ✅ All code generators produce valid, compilable code
- ✅ GUI is responsive and intuitive
- ✅ Can create, animate, and export GRAM cards
- ✅ Can layout 20×12 screen with GROM/GRAM
- ✅ Generated code works in real Intellivision projects
- ✅ Documentation complete
- ✅ Zero critical bugs

---

**Remember:** Tests first, implementation second. No exceptions! 🔴🟢🔵
