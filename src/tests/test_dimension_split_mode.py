import pytest
from unittest.mock import MagicMock

# Import the module to be tested
from ai.game_modes import GAME_MODES, DimensionSplitMode

def test_dimension_split_mode_initialization():
    mode = DimensionSplitMode()
    assert mode.name == "Dimension Split"
    assert "mirror" in mode.description.lower()

    # Ensure it is registered correctly
    assert "dimension_split" in GAME_MODES
    assert isinstance(GAME_MODES["dimension_split"], DimensionSplitMode)

def test_dimension_split_mirror_health_and_speed():
    mode = DimensionSplitMode()
    world = MagicMock()

    # Setup mock arena
    arena = MagicMock()
    arena.width = 1000.0
    world.arena = arena
    del world.leaderboard_manager
    del world.profile_manager
    del world.events
    world.weekly_mutator = ''

    # Create a mock ball that starts on the left side (x < 500)
    class MockBall:
        def __init__(self):
            self.alive = True
            self.x = 200.0
            self.hp = 100.0
            self.max_hp = 100.0
            self.base_speed = 100.0
            self.speed = 100.0
            self.invert_timer = 0.0

    ball1 = MockBall()

    balls = [ball1]

    # Tick 1: Initialize original side
    mode.tick(world, balls, 0.016)
    assert ball1.split_origin_side == "left"
    assert ball1._split_last_hp == 100.0

    # Move to the right side (wrong side)
    ball1.x = 800.0

    # Take damage (should heal instead)
    ball1.hp = 90.0
    # Gain speed (should lose speed instead)
    ball1.speed = 120.0

    # Tick 2: Should invert health and speed changes
    mode.tick(world, balls, 0.016)

    # HP should be inverted: instead of -10, we get +10 (but capped at max_hp which is 100)
    assert ball1.hp == 100.0

    # Speed should be mirrored: instead of +20, we get -20
    assert ball1.speed == 80.0

    # Invert timer should be set
    assert ball1.invert_timer >= 0.1

    # Tick 3: Move back to original side, take damage, should work normally
    ball1.x = 200.0
    ball1.hp = 90.0
    ball1.speed = 120.0

    mode.tick(world, balls, 0.016)

    # HP should remain 90
    assert ball1.hp == 90.0
    # Speed should remain 120
    assert ball1.speed == 120.0
