"""
Animation module for sequencing GRAM cards.

Animations are sequences of GRAM card slots with timing information.
Used for sprite animations, UI effects, and other dynamic graphics.
"""

from typing import List, Dict, Any, Optional


class Animation:
    """
    GRAM card animation sequence.

    Stores a sequence of card slots with frame durations.
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
        self._frames: List[Dict[str, int]] = []

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

    def add_frame(self, card_slot: int, duration: int) -> None:
        """
        Add frame to end of animation.

        Args:
            card_slot: GRAM card slot number (0-63)
            duration: How many frames to display this card
        """
        self._frames.append({"card_slot": card_slot, "duration": duration})

    def insert_frame(self, index: int, card_slot: int, duration: int) -> None:
        """
        Insert frame at specific position.

        Args:
            index: Position to insert at
            card_slot: GRAM card slot number
            duration: Frame duration
        """
        self._frames.insert(index, {"card_slot": card_slot, "duration": duration})

    def get_frame(self, index: int) -> Dict[str, int]:
        """
        Get frame data by index.

        Args:
            index: Frame index

        Returns:
            Dictionary with card_slot and duration
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
            "frames": self._frames.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Animation":
        """
        Create animation from dictionary.

        Args:
            data: Dictionary from to_dict()

        Returns:
            Animation instance
        """
        anim = cls(
            name=data["name"], fps=data.get("fps", 10), loop=data.get("loop", False)
        )

        # Handle new multi-track format with layers
        if "layers" in data:
            # Convert from multi-track to single track (use first visible layer)
            for layer in data["layers"]:
                if layer.get("visible", True):
                    # Found first visible layer, use its frames
                    for frame in layer.get("frames", []):
                        anim.add_frame(frame["card_slot"], frame["duration"])
                    break
            # If no visible layers, use first layer anyway
            if anim.frame_count == 0 and len(data["layers"]) > 0:
                for frame in data["layers"][0].get("frames", []):
                    anim.add_frame(frame["card_slot"], frame["duration"])
        # Handle old single-track format
        elif "frames" in data:
            for frame in data.get("frames", []):
                # Check if this is intermediate format (frames with layers)
                if "layers" in frame:
                    # Use first layer only
                    layers_list = frame.get("layers", [])
                    if layers_list:
                        card_slot = layers_list[0].get("card_slot", 0)
                    else:
                        card_slot = 0
                    duration = frame.get("duration", 5)
                    anim.add_frame(card_slot, duration)
                else:
                    # Standard old format
                    anim.add_frame(frame["card_slot"], frame["duration"])

        return anim
