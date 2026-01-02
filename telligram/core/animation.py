"""
Animation module for sequencing GRAM cards with multi-track layering.

Animations consist of multiple layer tracks (up to 8, matching Intellivision MOBs).
Each layer track has its own timeline with independent frames and durations.
Layers composite together during playback based on priority (0=top, 7=bottom).
"""

from typing import List, Dict, Any, Optional

# Maximum number of layer tracks (matches Intellivision's 8 MOBs)
MAX_LAYERS = 8


class Animation:
    """
    GRAM card animation with multi-track layering.

    Each animation has up to 8 independent layer tracks.
    Each layer track contains its own sequence of frames with durations.
    Layers composite together during playback (layer 0 = top priority).
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
        self._layers: List[Dict[str, Any]] = []
        # Each layer: {
        #   "visible": bool,
        #   "frames": [{"card_slot": int, "duration": int}, ...]
        # }

    @property
    def layer_count(self) -> int:
        """Number of layer tracks in animation"""
        return len(self._layers)

    @property
    def total_duration(self) -> int:
        """Total duration in frame ticks (longest layer)"""
        if not self._layers:
            return 0
        max_duration = 0
        for layer in self._layers:
            layer_duration = sum(f["duration"] for f in layer.get("frames", []))
            max_duration = max(max_duration, layer_duration)
        return max_duration

    @property
    def duration_seconds(self) -> float:
        """Total duration in seconds"""
        return self.total_duration / self.fps

    def add_layer(self, visible: bool = True) -> int:
        """
        Add a new layer track.

        Args:
            visible: Whether layer is visible

        Returns:
            Index of new layer, or -1 if at max layers
        """
        if len(self._layers) >= MAX_LAYERS:
            return -1

        self._layers.append({
            "visible": visible,
            "frames": []
        })
        return len(self._layers) - 1

    def remove_layer(self, layer_index: int) -> None:
        """
        Remove a layer track.

        Args:
            layer_index: Index of layer to remove
        """
        if 0 <= layer_index < len(self._layers):
            del self._layers[layer_index]

    def get_layer(self, layer_index: int) -> Optional[Dict[str, Any]]:
        """
        Get layer data.

        Args:
            layer_index: Layer index

        Returns:
            Layer dict or None if invalid index
        """
        if 0 <= layer_index < len(self._layers):
            return self._layers[layer_index]
        return None

    def set_layer_visibility(self, layer_index: int, visible: bool) -> None:
        """
        Set layer visibility.

        Args:
            layer_index: Layer index
            visible: Visibility state
        """
        if 0 <= layer_index < len(self._layers):
            self._layers[layer_index]["visible"] = visible

    def add_frame_to_layer(self, layer_index: int, card_slot: int, duration: int = 5) -> None:
        """
        Add frame to end of layer track.

        Args:
            layer_index: Layer index
            card_slot: GRAM card slot (0-63)
            duration: Frame duration in ticks
        """
        if 0 <= layer_index < len(self._layers):
            self._layers[layer_index]["frames"].append({
                "card_slot": card_slot,
                "duration": duration
            })

    def insert_frame_to_layer(self, layer_index: int, frame_index: int,
                             card_slot: int, duration: int = 5) -> None:
        """
        Insert frame at specific position in layer track.

        Args:
            layer_index: Layer index
            frame_index: Position to insert
            card_slot: GRAM card slot
            duration: Frame duration
        """
        if 0 <= layer_index < len(self._layers):
            frames = self._layers[layer_index]["frames"]
            frames.insert(frame_index, {
                "card_slot": card_slot,
                "duration": duration
            })

    def remove_frame_from_layer(self, layer_index: int, frame_index: int) -> None:
        """
        Remove frame from layer track.

        Args:
            layer_index: Layer index
            frame_index: Frame index to remove
        """
        if 0 <= layer_index < len(self._layers):
            frames = self._layers[layer_index]["frames"]
            if 0 <= frame_index < len(frames):
                del frames[frame_index]

    def get_frame_at_time(self, layer_index: int, time_ticks: int) -> Optional[int]:
        """
        Get which card is showing in a layer at a specific time.

        Args:
            layer_index: Layer index
            time_ticks: Time position in ticks

        Returns:
            Card slot number, or None if no card at that time
        """
        if not (0 <= layer_index < len(self._layers)):
            return None

        layer = self._layers[layer_index]
        if not layer.get("visible", True):
            return None

        frames = layer.get("frames", [])
        current_time = 0

        for frame in frames:
            duration = frame["duration"]
            if current_time <= time_ticks < current_time + duration:
                return frame["card_slot"]
            current_time += duration

        return None

    def get_all_cards_at_time(self, time_ticks: int) -> List[Optional[int]]:
        """
        Get all visible cards at a specific time (one per layer).

        Args:
            time_ticks: Time position in ticks

        Returns:
            List of card slots (one per layer, None if no card visible)
        """
        result = []
        for i in range(len(self._layers)):
            result.append(self.get_frame_at_time(i, time_ticks))
        return result

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
            "layers": [layer.copy() for layer in self._layers]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Animation':
        """
        Create animation from dictionary.

        Args:
            data: Dictionary from to_dict()

        Returns:
            Animation instance
        """
        anim = cls(
            name=data["name"],
            fps=data.get("fps", 60),
            loop=data.get("loop", False)
        )

        # Load layers if present (new format)
        if "layers" in data:
            anim._layers = [layer.copy() for layer in data["layers"]]
        # Backward compatibility: old single-track format
        elif "frames" in data:
            # Convert old format to single-layer format
            anim.add_layer(visible=True)
            for old_frame in data["frames"]:
                # Handle both old formats
                if "layers" in old_frame:
                    # Old format that had layers per frame - use first layer only
                    layers_list = old_frame.get("layers", [])
                    if layers_list:
                        card_slot = layers_list[0].get("card_slot", 0)
                    else:
                        card_slot = 0
                else:
                    # Very old format with direct card_slot
                    card_slot = old_frame.get("card_slot", 0)

                duration = old_frame.get("duration", 5)
                anim.add_frame_to_layer(0, card_slot, duration)

        return anim
