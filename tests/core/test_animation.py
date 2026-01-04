"""
Tests for Animation class.

Animations are sequences of GRAM card slots with frame timing.
"""

import pytest
from pathlib import Path
from telligram.core.animation import Animation
from telligram.core.project import Project
from telligram.core.card import GramCard


class TestAnimationCreation:
    """Test animation creation"""

    def test_create_empty_animation(self):
        """Should create empty animation"""
        anim = Animation(name="walk_cycle")
        assert anim.name == "walk_cycle"
        assert anim.frame_count == 0
        assert anim.fps == 10  # Default 10 FPS

    def test_create_animation_with_custom_fps(self):
        """Should create animation with custom FPS"""
        anim = Animation(name="run", fps=20)
        assert anim.fps == 20

    def test_fps_must_be_positive(self):
        """Should raise error for invalid FPS"""
        with pytest.raises(ValueError):
            Animation(name="test", fps=0)
        with pytest.raises(ValueError):
            Animation(name="test", fps=-5)


class TestAnimationFrames:
    """Test animation frame management"""

    def test_add_frame(self):
        """Should add frame to animation"""
        anim = Animation(name="test")
        anim.add_frame(card_slot=0, duration=1)
        assert anim.frame_count == 1

    def test_add_multiple_frames(self):
        """Should add multiple frames"""
        anim = Animation(name="walk")
        anim.add_frame(0, 2)  # card slot 0, 2 frames duration
        anim.add_frame(1, 2)
        anim.add_frame(2, 2)
        anim.add_frame(3, 2)
        assert anim.frame_count == 4

    def test_get_frame(self):
        """Should get frame data"""
        anim = Animation(name="test")
        anim.add_frame(5, 3)
        frame = anim.get_frame(0)
        assert frame["card_slot"] == 5
        assert frame["duration"] == 3

    def test_remove_frame(self):
        """Should remove frame from animation"""
        anim = Animation(name="test")
        anim.add_frame(0, 1)
        anim.add_frame(1, 1)
        anim.add_frame(2, 1)
        anim.remove_frame(1)
        assert anim.frame_count == 2
        assert anim.get_frame(0)["card_slot"] == 0
        assert anim.get_frame(1)["card_slot"] == 2

    def test_clear_all_frames(self):
        """Should clear all frames"""
        anim = Animation(name="test")
        anim.add_frame(0, 1)
        anim.add_frame(1, 1)
        anim.clear_frames()
        assert anim.frame_count == 0

    def test_insert_frame(self):
        """Should insert frame at specific position"""
        anim = Animation(name="test")
        anim.add_frame(0, 1)
        anim.add_frame(2, 1)
        anim.insert_frame(1, card_slot=1, duration=1)
        assert anim.frame_count == 3
        assert anim.get_frame(1)["card_slot"] == 1


class TestAnimationPlayback:
    """Test animation playback calculations"""

    def test_total_duration(self):
        """Should calculate total animation duration in frames"""
        anim = Animation(name="test")
        anim.add_frame(0, 2)
        anim.add_frame(1, 3)
        anim.add_frame(2, 1)
        assert anim.total_duration == 6  # 2 + 3 + 1

    def test_duration_in_seconds(self):
        """Should calculate duration in seconds"""
        anim = Animation(name="test", fps=10)
        anim.add_frame(0, 10)  # 10 frames at 10 FPS = 1 second
        anim.add_frame(1, 10)  # 10 frames at 10 FPS = 1 second
        assert anim.duration_seconds == 2.0

    def test_get_card_at_frame(self):
        """Should get which card slot is showing at given frame"""
        anim = Animation(name="test")
        anim.add_frame(0, 2)  # Frames 0-1
        anim.add_frame(1, 3)  # Frames 2-4
        anim.add_frame(2, 2)  # Frames 5-6

        assert anim.get_card_at_frame(0) == 0
        assert anim.get_card_at_frame(1) == 0
        assert anim.get_card_at_frame(2) == 1
        assert anim.get_card_at_frame(4) == 1
        assert anim.get_card_at_frame(5) == 2
        assert anim.get_card_at_frame(6) == 2

    def test_loop_mode(self):
        """Should handle looping animations"""
        anim = Animation(name="test", loop=True)
        anim.add_frame(0, 2)
        anim.add_frame(1, 2)

        # Frame 4 is past end, should loop back to start
        assert anim.get_card_at_frame(4, loop=True) == 0
        assert anim.get_card_at_frame(5, loop=True) == 0


class TestAnimationSerialization:
    """Test animation save/load"""

    def test_to_dict(self):
        """Should export animation to dictionary"""
        anim = Animation(name="walk", fps=12)
        anim.add_frame(0, 2)
        anim.add_frame(1, 2)

        data = anim.to_dict()
        assert data["name"] == "walk"
        assert data["fps"] == 12
        assert len(data["frames"]) == 2

    def test_from_dict(self):
        """Should load animation from dictionary"""
        data = {
            "name": "walk",
            "fps": 15,
            "loop": True,
            "frames": [
                {"card_slot": 0, "duration": 2},
                {"card_slot": 1, "duration": 2}
            ]
        }
        anim = Animation.from_dict(data)
        assert anim.name == "walk"
        assert anim.fps == 15
        assert anim.loop is True
        assert anim.frame_count == 2


class TestProjectWithAnimations:
    """Test integrating animations with projects"""

    def test_project_stores_animations(self):
        """Project should store animation list"""
        project = Project(name="game")
        assert hasattr(project, 'animations')
        assert len(project.animations) == 0

    def test_add_animation_to_project(self):
        """Should add animation to project"""
        project = Project(name="game")
        anim = Animation(name="player_walk")
        anim.add_frame(0, 2)
        project.add_animation(anim)
        assert len(project.animations) == 1
        assert project.animations[0].name == "player_walk"

    def test_save_project_with_animations(self, tmp_path):
        """Should save and load project with animations"""
        # Create project with animation
        project = Project(name="game")

        # Add some GRAM cards
        card1 = GramCard([0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF])
        card2 = GramCard([0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x00])
        project.set_card(0, card1)
        project.set_card(1, card2)

        # Add animation
        anim = Animation(name="test_anim", fps=12)
        anim.add_frame(0, 3)
        anim.add_frame(1, 3)
        project.add_animation(anim)

        # Save
        filepath = tmp_path / "test.telligram"
        project.save(filepath)

        # Load
        loaded = Project.load(filepath)
        assert len(loaded.animations) == 1
        assert loaded.animations[0].name == "test_anim"
        assert loaded.animations[0].fps == 12
        assert loaded.animations[0].frame_count == 2
