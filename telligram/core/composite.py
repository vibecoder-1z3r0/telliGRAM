"""
Layered animation composite module.

Composites allow combining multiple existing animations as independent layers.
Each layer references an existing Animation object and can be configured with
visibility, end behavior, and color override settings.
"""

from typing import List, Dict, Any, Optional


class LayerComposite:
    """
    Saved combination of animations as composited layers.

    Stores references to existing Animation objects rather than
    duplicating animation data. Each animation remains independently
    editable.
    """

    def __init__(self, name: str):
        """
        Create new layer composite.

        Args:
            name: Composite name
        """
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

    def add_layer(self, animation_name: str, visible: bool = True,
                  end_behavior: str = "loop", color_override: Optional[int] = None) -> None:
        """
        Add a layer to the composite.

        Args:
            animation_name: Name of animation to reference
            visible: Whether layer is included in composite
            end_behavior: What happens when animation ends ("loop", "hold", "hide")
            color_override: Optional Intellivision color index (0-15), None for original
        """
        if len(self.layers) >= 8:
            raise ValueError("Cannot add more than 8 layers")

        if end_behavior not in ("loop", "hold", "hide"):
            raise ValueError("end_behavior must be 'loop', 'hold', or 'hide'")

        if color_override is not None and not (0 <= color_override <= 15):
            raise ValueError("color_override must be 0-15 or None")

        self.layers.append({
            "animation_name": animation_name,
            "visible": visible,
            "end_behavior": end_behavior,
            "color_override": color_override
        })

    def remove_layer(self, index: int) -> None:
        """
        Remove layer at given index.

        Args:
            index: Layer index to remove
        """
        del self.layers[index]

    def update_layer(self, index: int, **kwargs) -> None:
        """
        Update layer settings.

        Args:
            index: Layer index
            **kwargs: Fields to update (animation_name, visible, end_behavior, color_override)
        """
        if index >= len(self.layers):
            raise IndexError(f"Layer index {index} out of range")

        layer = self.layers[index]

        if "animation_name" in kwargs:
            layer["animation_name"] = kwargs["animation_name"]
        if "visible" in kwargs:
            layer["visible"] = kwargs["visible"]
        if "end_behavior" in kwargs:
            if kwargs["end_behavior"] not in ("loop", "hold", "hide"):
                raise ValueError("end_behavior must be 'loop', 'hold', or 'hide'")
            layer["end_behavior"] = kwargs["end_behavior"]
        if "color_override" in kwargs:
            color = kwargs["color_override"]
            if color is not None and not (0 <= color <= 15):
                raise ValueError("color_override must be 0-15 or None")
            layer["color_override"] = color

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to JSON.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "layers": self.layers.copy(),
            "fps": self.fps,
            "loop": self.loop
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayerComposite':
        """
        Deserialize from JSON.

        Args:
            data: Dictionary from to_dict()

        Returns:
            LayerComposite instance
        """
        composite = cls(data["name"])
        composite.layers = data.get("layers", [])
        composite.fps = data.get("fps", 60)
        composite.loop = data.get("loop", False)
        return composite

    def get_card_at_frame(self, frame_num: int, project) -> List[Optional[int]]:
        """
        Get list of card slots to composite at given frame.

        Returns list of 8 card slots (one per layer, None if not visible/ended).
        Composites from bottom to top (index 0 = top priority).

        Args:
            frame_num: Frame number in composite timeline
            project: Project containing animations

        Returns:
            List of 8 card slots (None if layer not showing)
        """
        card_slots = [None] * 8

        for i, layer_config in enumerate(self.layers):
            if not layer_config.get("visible", True):
                continue

            # Get referenced animation
            anim_name = layer_config["animation_name"]
            animation = project.get_animation(anim_name)
            if animation is None:
                continue

            # Calculate which card to show based on end behavior
            end_behavior = layer_config.get("end_behavior", "loop")
            total_duration = animation.total_duration

            if total_duration == 0:
                continue

            # Determine frame position in this layer's animation
            if frame_num < total_duration:
                # Still playing
                card_slot = animation.get_card_at_frame(frame_num, loop=False)
            else:
                # Animation has ended
                if end_behavior == "loop":
                    # Loop back to beginning
                    card_slot = animation.get_card_at_frame(frame_num, loop=True)
                elif end_behavior == "hold":
                    # Hold on last frame
                    card_slot = animation.get_card_at_frame(total_duration - 1, loop=False)
                else:  # hide
                    # Hide layer
                    card_slot = None

            card_slots[i] = card_slot

        return card_slots

    def get_max_duration(self, project) -> int:
        """
        Get maximum duration across all layers.

        For non-looping layers, this is the longest animation duration.
        If all layers loop, returns the LCM of all durations.

        Args:
            project: Project containing animations

        Returns:
            Maximum frame duration
        """
        max_duration = 0

        for layer_config in self.layers:
            if not layer_config.get("visible", True):
                continue

            anim_name = layer_config["animation_name"]
            animation = project.get_animation(anim_name)
            if animation is None:
                continue

            duration = animation.total_duration
            if duration > max_duration:
                max_duration = duration

        return max_duration
