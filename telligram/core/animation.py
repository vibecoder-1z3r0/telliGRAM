"""
Animation module for sequencing GRAM cards.

Animations are sequences of GRAM card slots with timing information.
Supports layered frames (up to 8 layers) for MOB composition.
Used for sprite animations, UI effects, and other dynamic graphics.
"""

from typing import List, Dict, Any, Optional

# Maximum number of layers per frame (matches Intellivision's 8 MOBs)
MAX_LAYERS = 8


class Animation:
    """
    GRAM card animation sequence with layering support.

    Each frame can contain up to 8 layers (matching Intellivision's 8 MOBs).
    Layers have priority based on index (0 = top, 7 = bottom).
    Supports playback calculations and serialization.
    """

    def __init__(self, name: str, fps: int = 60, loop: bool = False):
        """
        Create new animation.

        Args:
            name: Animation name
            fps: Frames per second (default 60, matching STIC 60Hz)
            loop: Whether animation loops

        Raises:
            ValueError: If fps is not positive
        """
        if fps <= 0:
            raise ValueError("FPS must be positive")

        self.name = name
        self.fps = fps
        self.loop = loop
        self._frames: List[Dict[str, Any]] = []

    @property
    def frame_count(self) -> int:
        """Number of frames in animation"""
        return len(self._frames)

    @property
    def total_duration(self) -> int:
        """Total duration in frame counts"""
        return sum(frame["duration"] for frame in self._frames)

    @property
    def duration_seconds(self) -> float:
        """Total duration in seconds"""
        return self.total_duration / self.fps

    def add_frame(self, card_slot: Optional[int] = None, duration: int = 5, layers: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add frame to end of animation.

        Args:
            card_slot: GRAM card slot number (0-63) for backward compatibility
            duration: How many frames to display this card
            layers: List of layer dicts with 'card_slot' and 'visible' keys
        """
        if layers is None:
            # Backward compatibility: single card becomes layer 0
            if card_slot is not None:
                layers = [{"card_slot": card_slot, "visible": True}]
            else:
                layers = []

        self._frames.append({
            "layers": layers,
            "duration": duration
        })

    def insert_frame(self, index: int, card_slot: Optional[int] = None, duration: int = 5, layers: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Insert frame at specific position.

        Args:
            index: Position to insert at
            card_slot: GRAM card slot number for backward compatibility
            duration: Frame duration
            layers: List of layer dicts with 'card_slot' and 'visible' keys
        """
        if layers is None:
            # Backward compatibility: single card becomes layer 0
            if card_slot is not None:
                layers = [{"card_slot": card_slot, "visible": True}]
            else:
                layers = []

        self._frames.insert(index, {
            "layers": layers,
            "duration": duration
        })

    def get_frame(self, index: int) -> Dict[str, Any]:
        """
        Get frame data by index.

        Args:
            index: Frame index

        Returns:
            Dictionary with layers (list) and duration (int)
        """
        return self._frames[index]

    def remove_frame(self, index: int) -> None:
        """
        Remove frame from animation.

        Args:
            index: Frame index to remove
        """
        del self._frames[index]

    def clear_frames(self) -> None:
        """Remove all frames from animation"""
        self._frames.clear()

    def add_layer_to_frame(self, frame_index: int, card_slot: int, visible: bool = True, layer_index: Optional[int] = None) -> None:
        """
        Add a layer to a specific frame.

        Args:
            frame_index: Index of the frame
            card_slot: GRAM card slot number for the layer
            visible: Whether the layer is visible
            layer_index: Position to insert layer (None = append)
        """
        if frame_index >= len(self._frames):
            return

        frame = self._frames[frame_index]
        layers = frame.get("layers", [])

        if len(layers) >= MAX_LAYERS:
            return  # Already at max layers

        new_layer = {"card_slot": card_slot, "visible": visible}

        if layer_index is None:
            layers.append(new_layer)
        else:
            layers.insert(layer_index, new_layer)

        frame["layers"] = layers

    def remove_layer_from_frame(self, frame_index: int, layer_index: int) -> None:
        """
        Remove a layer from a specific frame.

        Args:
            frame_index: Index of the frame
            layer_index: Index of the layer to remove
        """
        if frame_index >= len(self._frames):
            return

        frame = self._frames[frame_index]
        layers = frame.get("layers", [])

        if 0 <= layer_index < len(layers):
            layers.pop(layer_index)
            frame["layers"] = layers

    def toggle_layer_visibility(self, frame_index: int, layer_index: int) -> None:
        """
        Toggle visibility of a layer in a specific frame.

        Args:
            frame_index: Index of the frame
            layer_index: Index of the layer
        """
        if frame_index >= len(self._frames):
            return

        frame = self._frames[frame_index]
        layers = frame.get("layers", [])

        if 0 <= layer_index < len(layers):
            layers[layer_index]["visible"] = not layers[layer_index].get("visible", True)

    def move_layer_up(self, frame_index: int, layer_index: int) -> None:
        """
        Move a layer up (higher priority) in a specific frame.

        Args:
            frame_index: Index of the frame
            layer_index: Index of the layer to move
        """
        if frame_index >= len(self._frames):
            return

        frame = self._frames[frame_index]
        layers = frame.get("layers", [])

        if layer_index > 0 and layer_index < len(layers):
            # Swap with layer above
            layers[layer_index], layers[layer_index - 1] = layers[layer_index - 1], layers[layer_index]

    def move_layer_down(self, frame_index: int, layer_index: int) -> None:
        """
        Move a layer down (lower priority) in a specific frame.

        Args:
            frame_index: Index of the frame
            layer_index: Index of the layer to move
        """
        if frame_index >= len(self._frames):
            return

        frame = self._frames[frame_index]
        layers = frame.get("layers", [])

        if layer_index >= 0 and layer_index < len(layers) - 1:
            # Swap with layer below
            layers[layer_index], layers[layer_index + 1] = layers[layer_index + 1], layers[layer_index]

    def duplicate_layer(self, frame_index: int, layer_index: int) -> None:
        """
        Duplicate a layer in a specific frame.

        Args:
            frame_index: Index of the frame
            layer_index: Index of the layer to duplicate
        """
        if frame_index >= len(self._frames):
            return

        frame = self._frames[frame_index]
        layers = frame.get("layers", [])

        if 0 <= layer_index < len(layers) and len(layers) < MAX_LAYERS:
            # Create copy of the layer
            new_layer = layers[layer_index].copy()
            # Insert after the original
            layers.insert(layer_index + 1, new_layer)
            frame["layers"] = layers

    def get_card_at_frame(self, frame_num: int, loop: bool = False) -> Optional[int]:
        """
        Get which card slot is showing at given frame number.

        Args:
            frame_num: Frame number in animation timeline
            loop: Whether to loop past end

        Returns:
            Card slot number, or None if past end and not looping
        """
        if self.frame_count == 0:
            return None

        # Handle looping
        if loop and self.total_duration > 0:
            frame_num = frame_num % self.total_duration

        # Find which animation frame contains this timeline frame
        current_frame = 0
        for anim_frame in self._frames:
            current_frame += anim_frame["duration"]
            if frame_num < current_frame:
                return anim_frame["card_slot"]

        return None  # Past end of animation

    def to_dict(self) -> Dict[str, Any]:
        """
        Export animation to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "fps": self.fps,
            "loop": self.loop,
            "frames": self._frames.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Animation':
        """
        Create animation from dictionary with backward compatibility.

        Supports both old format (single card_slot per frame) and new format (layers).

        Args:
            data: Dictionary from to_dict()

        Returns:
            Animation instance
        """
        anim = cls(
            name=data["name"],
            fps=data.get("fps", 10),
            loop=data.get("loop", False)
        )
        for frame in data.get("frames", []):
            # Backward compatibility: detect old format
            if "card_slot" in frame and "layers" not in frame:
                # Old format: convert single card to single layer
                layers = [{"card_slot": frame["card_slot"], "visible": True}]
                anim.add_frame(layers=layers, duration=frame["duration"])
            else:
                # New format: use layers directly
                layers = frame.get("layers", [])
                anim.add_frame(layers=layers, duration=frame["duration"])
        return anim
