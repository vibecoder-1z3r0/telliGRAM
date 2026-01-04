# telliGRAM Quick Start Guide

Get up and running with telliGRAM in 5 minutes!

## Prerequisites

- **Python 3.8 or higher** installed
- **pip** package manager
- **Git** (to clone the repository)

**Note:** PySide6 6.2.x is used for Python 3.8 compatibility. Python 3.9+ users will get newer versions automatically.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vibecoder-1z3r0/telliGRAM.git
cd telliGRAM
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

That's it! The only dependency is **PySide6** (Qt for Python).

### 3. Run telliGRAM

```bash
python3 -m telligram.main
```

## First Steps

### Creating Your First GRAM Card

1. **Launch the application**
   - The window opens with a 64-card grid on the left
   - Card #0 is selected by default

2. **Draw in the pixel editor**
   - Left panel shows the 8×8 pixel editor
   - **Click** to toggle individual pixels on/off
   - **Click and drag** to paint multiple pixels
   - **Right-click** to erase pixels

3. **Try the transformations**
   - **Clear Card** - Erase all pixels
   - **Flip H** - Flip horizontally (mirror)
   - **Flip V** - Flip vertically

4. **Select different cards**
   - Click any card in the 64-card grid
   - Each card can be edited independently
   - Cards are numbered 0-63 (GRAM 256-319)

### Saving Your Work

1. **Save Project**
   - Press `Ctrl+S` or use **File → Save Project**
   - Choose a filename (e.g., `my_game.telligram`)
   - All 64 cards are saved in JSON format

2. **Open Existing Project**
   - Press `Ctrl+O` or use **File → Open Project**
   - Select a `.telligram` file
   - All cards load automatically

## Exploring GROM Characters

The **GROM Browser** lets you reference all 256 built-in Intellivision characters.

1. **Open GROM Browser**
   - Click the **"GROM Browser"** tab on the right panel

2. **Browse Characters**
   - Scroll through all 256 GROM characters
   - Cards 0-94 are ASCII characters (letters, numbers, symbols)
   - Cards 95-255 are extended graphics (system-specific)

3. **Why Use GROM Browser?**
   - Avoid wasting GRAM slots on characters already in ROM
   - Reference for text and symbols
   - Save GRAM for custom game graphics

**Pro Tip:** Use GROM for text (like "SCORE", "LEVEL", etc.) and save your 64 GRAM slots for sprites and custom graphics!

## Creating Animations

The **Animation Timeline** lets you sequence GRAM cards for sprite animations.

### Basic Animation Workflow

1. **Open Timeline Editor**
   - Click the **"Animation Timeline"** tab on the right panel

2. **Create New Animation**
   - Click **"New"** button
   - Animation appears in the list (e.g., "Animation_1")

3. **Add Frames**
   - Click a GRAM card in the grid (left panel)
   - Set **Duration** (how many frames to show)
   - Click **"Add Frame"** button
   - Repeat for all frames in your animation

4. **Preview Animation**
   - Click **"▶ Play"** to preview
   - Adjust **FPS** (frames per second) for speed
   - Click **"⏹ Stop"** to reset

5. **Save Animation**
   - Press `Ctrl+S` to save project
   - Animations are saved with your project

### Example: Walk Cycle Animation

```
1. Create 4 GRAM cards with different walk poses (cards 0-3)
2. Create new animation named "walk_cycle"
3. Add frames:
   - Card 0, Duration: 2
   - Card 1, Duration: 2
   - Card 2, Duration: 2
   - Card 3, Duration: 2
4. Set FPS to 12
5. Click Play to preview
6. Save project!
```

## Keyboard Shortcuts

- `Ctrl+N` - New project
- `Ctrl+O` - Open project
- `Ctrl+S` - Save project
- `Ctrl+Shift+S` - Save As
- `Ctrl+Shift+C` - Clear current card
- `Ctrl+Q` - Quit

## File Format

telliGRAM saves projects as **JSON files** with `.telligram` extension.

**Example:**
```json
{
  "name": "my_game",
  "author": "Your Name",
  "version": "1.0",
  "cards": [
    {
      "label": "player_ship",
      "data": [255, 129, 129, 129, 129, 129, 129, 255]
    },
    null,
    ...
  ],
  "animations": [
    {
      "name": "walk_cycle",
      "fps": 12,
      "frames": [...]
    }
  ]
}
```

**Benefits:**
- Human-readable
- Git-friendly (track changes, merge, diff)
- Easy to edit manually if needed
- Cross-platform compatible

## Tips & Tricks

### Drawing Tips

- **Use symmetry** - Create half the sprite, then use Flip H or Flip V
- **Start with outlines** - Draw borders first, fill in details
- **Reference GROM** - Check GROM browser for letter/number shapes
- **Test early** - Preview your sprites in animation timeline

### Organization Tips

- **Name your animations** - Change "Animation_1" to "player_walk"
- **Use consistent slots** - Keep related sprites in adjacent slots
- **Document your cards** - Use descriptive labels (future feature)
- **Save often** - Press `Ctrl+S` frequently

### Performance Tips

- **GRAM loading limit** - Intellivision can load ~18 cards per frame
- **Plan animations** - Group cards used in same animations
- **Reuse cards** - Same card can appear in multiple animations

## Troubleshooting

### Application won't start

```bash
# Make sure PySide6 is installed
pip install PySide6>=6.2.0

# Try running again
python3 -m telligram.main
```

### Tests failing

```bash
# Install dev requirements
pip install -r requirements-dev.txt

# Run tests
python3 -m pytest tests/
```

### Graphics look wrong

- Make sure you're using **1-bit graphics** (on/off only)
- Each card is **8×8 pixels** (8 bytes, 1 byte per row)
- Preview in pixel editor to verify

## Next Steps

1. **Create a simple sprite** - Draw a player character
2. **Make a walk cycle** - 4-frame animation
3. **Explore GROM** - See what's already available
4. **Save your project** - Keep your work safe!

## Getting Help

- **Documentation:** See `docs/` folder for detailed specs
- **Issues:** https://github.com/vibecoder-1z3r0/telliGRAM/issues
- **Discussions:** https://github.com/vibecoder-1z3r0/telliGRAM/discussions

## What's Next?

**Coming Soon:**
- IntyBASIC code export (BITMAP format)
- Assembly code export (DECLE format)
- Screen layout editor (20×12 BACKTAB)
- Sprite sheet import
- Undo/redo system

---

**Happy GRAM card creation!** 🎮✨

Now go make some awesome Intellivision graphics!
