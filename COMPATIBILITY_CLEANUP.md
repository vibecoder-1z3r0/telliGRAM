# Animation Format Compatibility Cleanup

## Current Situation

After rolling back from multi-track layer implementation, we have backward compatibility code that creates technical debt and should be cleaned up in a future version.

## The Problem

**animation.py** currently has compatibility code in `from_dict()` that can read THREE different formats:

1. **Original simple format** (what we want):
```json
{
  "name": "Animation 1",
  "fps": 60,
  "loop": false,
  "frames": [
    {"card_slot": 0, "duration": 5},
    {"card_slot": 1, "duration": 5}
  ]
}
```

2. **Intermediate "layers per frame" format** (failed implementation):
```json
{
  "name": "Animation 1",
  "fps": 60,
  "loop": false,
  "frames": [
    {
      "duration": 5,
      "layers": [
        {"card_slot": 0, "visible": true}
      ]
    }
  ]
}
```

3. **Multi-track format** (failed implementation):
```json
{
  "name": "Animation 1",
  "fps": 60,
  "loop": false,
  "layers": [
    {
      "visible": true,
      "frames": [
        {"card_slot": 0, "duration": 5}
      ]
    }
  ]
}
```

## Current Code Location

**File**: `telligram/core/animation.py`
**Method**: `Animation.from_dict()` (lines 147-194)

The compatibility code converts formats #2 and #3 back to format #1 during loading.

## Why This Matters

- **Technical Debt**: Maintaining 3 format parsers when we only need 1
- **Confusion**: Future developers won't know why this code exists
- **Performance**: Unnecessary format detection and conversion
- **Testing**: Need to test 3 formats instead of 1

## Cleanup Plan (Future Task)

When ready to clean this up:

1. **Wait Period**: Keep compatibility code for at least one release cycle to ensure users can migrate their save files
2. **User Communication**: Warn users in release notes that old formats will be deprecated
3. **Migration Tool**: Consider adding a one-time migration script that converts old save files
4. **Code Removal**: Remove the compatibility handling for formats #2 and #3
5. **Simplify**: Return `from_dict()` to only handle format #1

## Simplified Target Code

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'Animation':
    """Create animation from dictionary."""
    anim = cls(
        name=data["name"],
        fps=data.get("fps", 10),
        loop=data.get("loop", False)
    )
    for frame in data.get("frames", []):
        anim.add_frame(frame["card_slot"], frame["duration"])
    return anim
```

## When to Clean Up

- After confirming no users have save files in formats #2 or #3
- When starting a new major version (e.g., v2.0.0)
- After implementing proper format migration tooling
- When adding new features that would complicate the compatibility layer

## Related Files

- `telligram/core/animation.py` - Contains compatibility code
- `telligram/core/project.py` - Save/load logic
- User save files (*.tgram) - May contain old formats

## Notes

The `to_dict()` method always writes format #1 (simple format), so saving any project will normalize it to the current format. This means users can "migrate" by simply opening and saving their projects.
