# Known Issues

This document tracks known bugs and issues that need to be addressed in future updates.

## Composite Sprite Animator (CSA)

### High Priority

- **Animation "ends" behavior not honored**: The end behavior setting (loop, hold, clear) is no longer being respected during playback
- **Stop and Rewind do the same thing**: Both buttons currently rewind to frame 0; Stop should pause at current frame

### Low Priority / Needs Discussion

- **Frame counter label (F: 000/000)**: Question whether this label is necessary in the CSA playback controls

## Export Functionality

### Medium Priority

- **IntyBASIC Data export shows same output as Visual**: When exporting "Export all GRAM Cards" or "Export Animation", selecting "IntyBASIC (Data)" format produces the same output as "IntyBASIC (Visual)" instead of showing DATA format
  - Individual card export works correctly
  - Need to implement separate data generators for bulk exports and animations

- **Export individual cards dialog has inconsistent appearance**: The export dialog for individual cards (right-click → Export) has a different visual style/title format compared to "Export all GRAM Cards" and "Export Animation" dialogs
  - Consider standardizing title format (e.g., "Export GRAM Card #5" vs "Export Card #5")

## Future Enhancements

_(Items to be added as needed)_
