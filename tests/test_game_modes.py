import pytest
from ai.game_modes import MazeSafeZoneMode

def test_dummy_game_modes_coverage():
    mode = MazeSafeZoneMode()
    assert mode.name == "Maze Safe Zone"

def test_sweeping_lasers_mode():
    from unittest.mock import MagicMock
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["sweeping_lasers"]
    world = MagicMock()
    world.arena.width = 1000
    world.arena.height = 1000
    world.arena.hazards = []
    world.leaderboard_manager.data.get.return_value = 1

    b1 = MagicMock()
    b1.alive = True
    b1.x = 500
    b1.y = 50
    b1.hp = 100
    b1.take_damage = MagicMock()

    b2 = MagicMock()
    b2.alive = True
    b2.x = 100
    b2.y = 100
    b2.hp = 100
    b2.take_damage = MagicMock()

    mode.setup(world, [b1, b2])

    assert len(world.arena.hazards) == 1
    assert mode.sweep_timer == 0.0

    mode.tick(world, [b1, b2], 0.0)

    # Check if b1 takes damage because the laser should hit it
    assert b1.take_damage.call_count > 0 or b1.hp < 100
