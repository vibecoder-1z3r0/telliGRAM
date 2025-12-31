"""Project model for telliGRAM - handles save/load"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from .card import GramCard
from .animation import Animation


class Project:
    """
    telliGRAM Project - contains all GRAM cards and project metadata

    File format: JSON (.telligram extension)
    """

    MAX_CARDS = 64  # Maximum GRAM cards (256-319)

    def __init__(
        self,
        name: str,
        author: str = "",
        description: str = "",
        version: str = "1.0"
    ):
        """
        Initialize new project

        Args:
            name: Project name
            author: Project author
            description: Project description
            version: Project version
        """
        self.name = name
        self.author = author
        self.description = description
        self.version = version

        # Initialize 64 empty card slots
        self.cards: List[Optional[GramCard]] = [None] * self.MAX_CARDS

        # Initialize animations list
        self.animations: List[Animation] = []

    def get_card(self, slot: int) -> Optional[GramCard]:
        """
        Get card at slot

        Args:
            slot: Slot number (0-63)

        Returns:
            GramCard or None if empty

        Raises:
            IndexError: If slot out of range
        """
        if not (0 <= slot < self.MAX_CARDS):
            raise IndexError(f"Card slot must be 0-{self.MAX_CARDS-1}, got {slot}")
        return self.cards[slot]

    def set_card(self, slot: int, card: GramCard) -> None:
        """
        Set card at slot

        Args:
            slot: Slot number (0-63)
            card: GramCard to set

        Raises:
            IndexError: If slot out of range
        """
        if not (0 <= slot < self.MAX_CARDS):
            raise IndexError(f"Card slot must be 0-{self.MAX_CARDS-1}, got {slot}")
        self.cards[slot] = card

    def clear_card(self, slot: int) -> None:
        """
        Clear card at slot

        Args:
            slot: Slot number (0-63)
        """
        if not (0 <= slot < self.MAX_CARDS):
            raise IndexError(f"Card slot must be 0-{self.MAX_CARDS-1}, got {slot}")
        self.cards[slot] = None

    def get_used_slots(self) -> List[int]:
        """
        Get list of used slot numbers

        Returns:
            List of slot numbers that have cards
        """
        return [i for i, card in enumerate(self.cards) if card is not None]

    def get_card_count(self) -> int:
        """
        Count number of used cards

        Returns:
            Number of non-empty slots
        """
        return sum(1 for card in self.cards if card is not None)

    def add_animation(self, animation: Animation) -> None:
        """
        Add animation to project

        Args:
            animation: Animation to add
        """
        self.animations.append(animation)

    def to_dict(self) -> Dict[str, Any]:
        """
        Export project as dictionary for JSON serialization

        Returns:
            Dictionary containing all project data
        """
        return {
            "name": self.name,
            "author": self.author,
            "description": self.description,
            "version": self.version,
            "cards": [
                card.to_dict() if card is not None else None
                for card in self.cards
            ],
            "animations": [
                anim.to_dict() for anim in self.animations
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """
        Create project from dictionary

        Args:
            data: Dictionary from JSON

        Returns:
            New Project instance
        """
        project = cls(
            name=data["name"],
            author=data.get("author", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0")
        )

        # Load cards
        cards_data = data.get("cards", [])
        for i, card_data in enumerate(cards_data):
            if card_data is not None:
                project.cards[i] = GramCard.from_dict(card_data)

        # Load animations
        animations_data = data.get("animations", [])
        for anim_data in animations_data:
            project.animations.append(Animation.from_dict(anim_data))

        return project

    def save(self, filepath: Path) -> None:
        """
        Save project to JSON file

        Args:
            filepath: Path to save to (.telligram file)
        """
        filepath = Path(filepath)

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save as formatted JSON (human-readable)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> 'Project':
        """
        Load project from JSON file

        Args:
            filepath: Path to load from

        Returns:
            Loaded Project instance

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Project file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        return cls.from_dict(data)

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"Project(name='{self.name}', cards={self.get_card_count()}/{self.MAX_CARDS})"
