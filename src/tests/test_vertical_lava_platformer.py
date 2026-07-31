from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES
import pytest

def test_vertical_lava_platformer_mode():
    mode = GAME_MODES.get("vertical_lava_platformer")
    assert mode is not None
    assert "lava" in mode.description.lower()
    assert "low_gravity" in mode.mutators

    world = MagicMock()
    world.arena = MagicMock()
    world.arena.height = 1000.0
    world.arena.width = 1000.0
    world.arena.hazards = []

    lm = MagicMock()
    lm.data = {"current_season": 1}
    world.leaderboard_manager = lm

    # Setup mode
    mode.setup(world, [])
    assert len(world.arena.hazards) == 15
    for hazard in world.arena.hazards:
        assert hazard.kind == "jump_pad"

    ball1 = MagicMock(alive=True, y=960.0, hp=100.0)
    ball2 = MagicMock(alive=True, y=400.0, hp=100.0)

    # Tick 1: Initialize
    mode.apply_dynamic_traits(world, [ball1, ball2], 1.0)
    assert mode.lava_y == 1000.0 - 15.0

    # Submerge ball 1
    mode.apply_dynamic_traits(world, [ball1, ball2], 4.0)

    # Check HP
    assert ball1.hp == 0.0
    assert not ball1.alive
    assert ball1.killer == "lava"

    assert ball2.hp == 100.0
    assert ball2.alive
