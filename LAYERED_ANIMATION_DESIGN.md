# Layered Animation Composite Design

## Overview

Implement layered animation compositing by allowing users to combine multiple existing animations as independent layers. Each layer references an existing Animation object and can be toggled on/off with configurable end behavior.

**Key Principle**: Keep animations simple (single-track) and reusable. Composites are just lightweight references to existing animations.

## UI Design

### Single Layer Mode (Default)

When no additional layers are added, show the standard timeline editor:

```
┌─ Animation Timeline ──────────────────────────┐
│ Animation: [walk_cycle ▼] [New] [Rename]     │
│ ┌──────────────────────────────────────────┐ │
│ │ [Timeline: frame thumbnails...]          │ │
│ └──────────────────────────────────────────┘ │
│ [▶] [⏹] [⏮] Speed: [...] Loop: [✓]          │
│ [Preview]                                     │
│                                                │
│ [+ Add Layer]  ← Shows multi-layer mode       │
└────────────────────────────────────────────────┘
```

### Multi-Layer Mode

After clicking "Add Layer", expand to show multiple layer editors plus composite preview:

```
┌─ Layer 1 ─────────────────────────────────────┐
│ Animation: [walk_cycle ▼]                     │
│ ┌──────────────────────────────────────────┐ │
│ │ [Timeline: walk frames...]               │ │
│ └──────────────────────────────────────────┘ │
│ [▶] [⏹] Speed: [...] Loop: [✓]   [Preview]  │
└────────────────────────────────────────────────┘

┌─ Layer 2 ─────────────────────────────────────┐
│ Animation: [arms_swing ▼]                     │
│ ┌──────────────────────────────────────────┐ │
│ │ [Timeline: arm frames...]                │ │
│ └──────────────────────────────────────────┘ │
│ [▶] [⏹] Speed: [...] Loop: [✓]   [Preview]  │
└────────────────────────────────────────────────┘

... (up to 8 layers total)

┌─ Combined Preview ────────────────────────────┐
│ Composite: [(new) ▼] [Save] [Delete]         │
│                                                │
│ Layers to composite:                           │
│ [✓] Layer 1 (walk_cycle)                      │
│     Color: [Original▼] When ends: [Loop▼]    │
│ [✓] Layer 2 (arms_swing)                      │
│     Color: [Red     ▼] When ends: [Hold▼]    │
│ [ ] Layer 3 (empty)                            │
│     Color: [Original▼] When ends: [Loop▼]    │
│ ... up to 8                                    │
│                                                │
│ [▶ Play] [⏹ Stop] [⏮ Rewind]                 │
│ Speed: [slider]  Loop: [✓]                    │
│                                                │
│ ┌─────────────────┐                           │
│ │   Composite     │  ← Shows all checked     │
│ │   Preview       │     layers with colors    │
│ └─────────────────┘                           │
└────────────────────────────────────────────────┘

[+ Add Layer] [- Remove Layer]
```

## Managing Multiple Composites

Projects can save **multiple composite configurations**:

### Composite Selector Dropdown
- Shows all saved composites in the project
- Plus "(new)" option for creating new composites
- Selecting a composite loads its layer configuration
- **Example composites**:
  - "Character Walk + Attack"
  - "Character Run + Jump"
  - "Enemy Patrol + Idle"
  - "Boss Battle - Phase 1"

### Workflow
1. **Create**: Configure layers, click [Save], enter name
2. **Load**: Select from dropdown, layers auto-configure
3. **Edit**: Load composite, modify layers, click [Save] to update
4. **Delete**: Select composite, click [Delete] button

### Benefits
- Quickly switch between different layer combinations
- Test multiple character/enemy configurations
- Save variations for different game states
- Reuse layer setups across sessions

## Playback Behavior

### Individual Layer Playback

Each layer has independent playback controls for **testing**:
- Play/stop that layer's animation alone
- Adjust speed for that layer
- Preview shows only that layer's cards
- **Does NOT affect other layers or composite**

### Composite Playback (Option B - Synchronized)

When Play is clicked on the Combined Preview:

1. **Sync all checked layers** to frame 0
2. **All checked layers play together** using the composite's speed setting
3. **Individual layer timelines show current position** as they advance
4. **Composite preview shows composited result** at each frame
5. **When composite stops, all layers stop**

This allows testing individual layers separately, then seeing the final synchronized result in the composite view.

## Layer End Behavior

When animations have different durations, each layer can specify what happens when it reaches the end:

### Loop
- Animation restarts from frame 0
- Continues playing indefinitely
- **Example**: Background animation that continuously cycles

### Hold Last Frame
- Animation stops on its final card
- Continues displaying that card until composite stops
- **Example**: Character that reaches a pose and holds it

### Hide
- Animation becomes transparent after ending
- No card is composited from this layer
- **Example**: Effect that disappears after playing once

## Layer Color Override

Each layer in the composite can override the color of its animation's cards:

### Original (No Override)
- Uses the card's original color as designed
- **Default behavior** when no override is selected
- Animation looks exactly as it does in the timeline editor

### Color Override Selected
- Replaces all card pixels with the selected Intellivision color (0-15)
- Maintains pixel on/off pattern from original card
- Only changes the color, not the shape
- **Example Uses**:
  - Same walk animation in different colors for multiple characters
  - Recolor effect animations to match different themes
  - Create color variations without duplicating animations

### Color Dropdown Options
- "Original" - No override (default)
- "Black" through "White" - All 16 Intellivision colors
- Uses jzIntv accurate color palette
- Preview updates immediately when color is changed

## Data Structures

### LayerComposite Class

```python
class LayerComposite:
    """
    Saved combination of animations as composited layers.

    Stores references to existing Animation objects rather than
    duplicating animation data. Each animation remains independently
    editable.
    """

    def __init__(self, name: str):
        self.name = name
        self.layers: List[Dict[str, Any]] = []
        # Each layer:
        # {
        #   "animation_name": str,      # Reference to existing animation
        #   "visible": bool,            # Include in composite
        #   "end_behavior": str,        # "loop", "hold", or "hide"
        #   "color_override": int|None  # Intellivision color index (0-15), None = original
        # }
        self.fps: int = 60              # Composite playback speed
        self.loop: bool = False         # Loop entire composite

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON"""
        return {
            "name": self.name,
            "layers": self.layers.copy(),
            "fps": self.fps,
            "loop": self.loop
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayerComposite':
        """Deserialize from JSON"""
        composite = cls(data["name"])
        composite.layers = data.get("layers", [])
        composite.fps = data.get("fps", 60)
        composite.loop = data.get("loop", False)
        return composite

    def get_card_at_frame(self, frame_num: int, project: Project) -> List[Optional[int]]:
        """
        Get list of card slots to composite at given frame.

        Returns list of 8 card slots (one per layer, None if not visible/ended).
        Composites from bottom to top (index 0 = top priority).
        """
        # Implementation details...
```

### Project Integration

Add composites list to Project class:

```python
class Project:
    def __init__(self):
        # ... existing fields ...
        self.composites: List[LayerComposite] = []

    def add_composite(self, composite: LayerComposite):
        """Add a saved composite"""
        self.composites.append(composite)

    def get_composite(self, name: str) -> Optional[LayerComposite]:
        """Find composite by name"""
        for composite in self.composites:
            if composite.name == name:
                return composite
        return None
```

## Rendering Logic

### Compositing Cards

At each frame position, composite visible layers from bottom to top:

```python
def render_composite_frame(composite: LayerComposite, frame_num: int, project: Project):
    """
    Render composite frame by layering cards with color overrides.

    Draws layers in reverse order (index 7 to 0) so index 0 has top priority.
    Only draws non-transparent pixels, allowing layers to show through.
    Applies color override if specified for the layer.
    """
    card_slots = composite.get_card_at_frame(frame_num, project)

    # Draw from bottom layer to top
    for i in reversed(range(8)):
        if card_slots[i] is None:
            continue

        card = project.get_card(card_slots[i])
        if card is None:
            continue

        # Determine color to use
        layer_config = composite.layers[i]
        if layer_config.get("color_override") is not None:
            # Use override color
            color = layer_config["color_override"]
        else:
            # Use card's original color
            color = card.color

        # Draw only non-transparent pixels
        for y in range(8):
            for x in range(8):
                if card.get_pixel(x, y):
                    # Draw pixel in determined color
                    draw_pixel(x, y, color)
```

## Benefits of This Approach

1. **Simplicity**: Each animation stays simple and single-track
2. **Reusability**: Same animation can be used in multiple composites
3. **Editability**: Edit an animation and all composites using it update
4. **Flexibility**: Mix and match animations easily
5. **Lightweight**: Composites are just references, no data duplication
6. **Backward Compatible**: Existing animations work unchanged
7. **No Complex Data Model**: No multi-track timeline format needed
8. **Color Flexibility**: Recolor animations per-layer without duplication

## Implementation Plan

### Phase 1: Data Model
1. Create `LayerComposite` class in `telligram/core/composite.py`
2. Add `composites` list to `Project` class
3. Implement serialization (to_dict/from_dict)
4. Add composite save/load to project file format

### Phase 2: Composite Preview Widget
1. Create `CompositePreviewWidget` in new file
2. Implement layer selection checkboxes
3. Add end-behavior dropdowns per layer
4. Create composite playback controls
5. Implement synchronized layer playback
6. Implement card compositing renderer

### Phase 3: Multi-Layer UI
1. Modify TimelineEditorWidget to support layer mode
2. Add "Add Layer" / "Remove Layer" buttons
3. Show/hide layers based on layer count
4. Show/hide composite preview when layers > 1
5. Create multiple TimelineEditorWidget instances for layers

### Phase 4: Integration
1. Wire up composite preview to layer selections
2. Implement synchronized playback across layers
3. Add "Save as Composite" functionality
4. Add composite selector dropdown
5. Allow loading saved composites

### Phase 5: Testing & Polish
1. Test with animations of different durations
2. Test all end behaviors (loop, hold, hide)
3. Test composite saving/loading
4. Polish UI layout and spacing
5. Add tooltips and help text

## Open Questions

- Should composite preview be on right side or bottom of window?
- Should we limit number of saved composites?
- Should composites have their own tab in the main window?
- Can a composite reference another composite (nested composites)?
- Should we add layer opacity controls in future?

## Future Enhancements

Possible features for later versions:

- Layer opacity/transparency controls
- Layer blend modes (normal, add, multiply, etc.)
- Layer position offsets (X/Y coordinates)
- Layer z-ordering controls
- Export composite to single merged animation
- Composite preview scrubber/timeline
- Copy composite to new project
