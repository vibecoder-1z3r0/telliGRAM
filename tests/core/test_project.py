"""
Tests for Project class (save/load functionality)

Following TDD: Write tests FIRST, then implement
"""
import pytest
import json
import tempfile
from pathlib import Path
from telligram.core.project import Project
from telligram.core.card import GramCard


class TestProjectCreation:
    """Test basic Project creation"""

    def test_create_empty_project(self):
        """Should create empty project with metadata"""
        project = Project(name="test_game")
        assert project.name == "test_game"
        assert len(project.cards) == 64  # All 64 GRAM slots
        assert all(card is None for card in project.cards)

    def test_project_with_metadata(self):
        """Should store project metadata"""
        project = Project(
            name="space_quest",
            author="Test Author",
            description="A space game"
        )
        assert project.name == "space_quest"
        assert project.author == "Test Author"
        assert project.description == "A space game"


class TestProjectCardManagement:
    """Test managing GRAM cards in project"""

    def test_set_card(self):
        """Should set card at specific slot"""
        project = Project(name="test")
        card = GramCard([0xFF] * 8)
        card.label = "test_card"

        project.set_card(0, card)
        assert project.get_card(0) == card
        assert project.get_card(0).label == "test_card"

    def test_get_empty_card_returns_none(self):
        """Should return None for empty slot"""
        project = Project(name="test")
        assert project.get_card(0) is None

    def test_set_card_out_of_range_raises_error(self):
        """Should raise IndexError for invalid slot"""
        project = Project(name="test")
        card = GramCard([0xFF] * 8)

        with pytest.raises(IndexError):
            project.set_card(64, card)  # Max is 63
        with pytest.raises(IndexError):
            project.set_card(-1, card)

    def test_clear_card(self):
        """Should clear card at slot"""
        project = Project(name="test")
        card = GramCard([0xFF] * 8)
        project.set_card(0, card)

        project.clear_card(0)
        assert project.get_card(0) is None

    def test_get_used_slots(self):
        """Should return list of used slot numbers"""
        project = Project(name="test")
        project.set_card(0, GramCard([0xFF] * 8))
        project.set_card(5, GramCard([0xAA] * 8))
        project.set_card(10, GramCard([0x55] * 8))

        used = project.get_used_slots()
        assert used == [0, 5, 10]

    def test_get_card_count(self):
        """Should count number of used cards"""
        project = Project(name="test")
        assert project.get_card_count() == 0

        project.set_card(0, GramCard([0xFF] * 8))
        project.set_card(1, GramCard([0xAA] * 8))
        assert project.get_card_count() == 2


class TestProjectSaveLoad:
    """Test saving and loading projects as JSON"""

    def test_save_to_json(self, tmp_path):
        """Should save project to JSON file"""
        project = Project(name="test_game", author="Test")

        # Add some cards
        card1 = GramCard([0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF])
        card1.label = "player_ship"
        project.set_card(0, card1)

        card2 = GramCard([0xAA] * 8)
        card2.label = "enemy"
        project.set_card(5, card2)

        # Save to file
        filepath = tmp_path / "test.telligram"
        project.save(filepath)

        # Verify file exists and is valid JSON
        assert filepath.exists()
        with open(filepath, 'r') as f:
            data = json.load(f)
            assert data["name"] == "test_game"
            assert data["author"] == "Test"
            assert len(data["cards"]) == 64

    def test_load_from_json(self, tmp_path):
        """Should load project from JSON file"""
        # Create and save project
        project1 = Project(name="test_game", author="Test Author")
        card = GramCard([0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00])
        card.label = "test_card"
        project1.set_card(0, card)

        filepath = tmp_path / "test.telligram"
        project1.save(filepath)

        # Load project
        project2 = Project.load(filepath)

        assert project2.name == "test_game"
        assert project2.author == "Test Author"
        assert project2.get_card_count() == 1

        loaded_card = project2.get_card(0)
        assert loaded_card is not None
        assert loaded_card.label == "test_card"
        assert loaded_card.to_bytes() == [0xFF, 0x81, 0x00, 0x42, 0x00, 0x00, 0x00, 0x00]

    def test_save_preserves_all_metadata(self, tmp_path):
        """Should preserve all project metadata on save/load"""
        project1 = Project(
            name="space_quest",
            author="John Doe",
            description="Epic space adventure",
            version="1.0"
        )

        filepath = tmp_path / "test.telligram"
        project1.save(filepath)

        project2 = Project.load(filepath)
        assert project2.name == "space_quest"
        assert project2.author == "John Doe"
        assert project2.description == "Epic space adventure"
        assert project2.version == "1.0"

    def test_save_empty_project(self, tmp_path):
        """Should save/load project with no cards"""
        project1 = Project(name="empty_project")

        filepath = tmp_path / "empty.telligram"
        project1.save(filepath)

        project2 = Project.load(filepath)
        assert project2.name == "empty_project"
        assert project2.get_card_count() == 0

    def test_load_invalid_file_raises_error(self):
        """Should raise error for invalid file"""
        with pytest.raises(FileNotFoundError):
            Project.load(Path("nonexistent.telligram"))

    def test_json_format_is_readable(self, tmp_path):
        """JSON file should be human-readable"""
        project = Project(name="test")
        card = GramCard([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00])
        card.label = "test_card"
        project.set_card(0, card)

        filepath = tmp_path / "test.telligram"
        project.save(filepath)

        # Read and verify JSON is formatted nicely
        with open(filepath, 'r') as f:
            content = f.read()
            assert '"name": "test"' in content
            assert '"test_card"' in content
            # Should have indentation (not minified)
            assert '\n' in content


class TestProjectFileFormat:
    """Test JSON file format specification"""

    def test_json_structure(self, tmp_path):
        """Verify JSON structure matches specification"""
        project = Project(name="test", author="author", version="1.0")
        card = GramCard([0xFF] * 8)
        card.label = "card1"
        project.set_card(0, card)

        filepath = tmp_path / "test.telligram"
        project.save(filepath)

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Required keys
        assert "name" in data
        assert "author" in data
        assert "version" in data
        assert "cards" in data

        # Cards should be array of 64 items
        assert isinstance(data["cards"], list)
        assert len(data["cards"]) == 64

        # Card at index 0 should have data
        assert data["cards"][0] is not None
        assert "label" in data["cards"][0]
        assert "data" in data["cards"][0]

        # Empty slots should be null
        assert data["cards"][1] is None
