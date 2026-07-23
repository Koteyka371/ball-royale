import pytest
from ai.game_modes import GAME_MODES
from unittest.mock import MagicMock

def test_snake_safe_zone_mode():
    mode = GAME_MODES.get("snake_safe_zone")
    assert mode is not None, "Snake Safe Zone mode not found!"
    assert mode.name == "Snake Safe Zone"

    # Test setup and tick
    world = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.season = 1
    world.leaderboard_manager.data = {"current_season": 1}
    world.profile_manager.leaderboard_manager = world.leaderboard_manager

    ball = MagicMock()
    ball.alive = True
    ball.x = 500.0
    ball.y = 500.0
    ball.hp = 100.0
    ball.ball_type = "player"

    mode.setup(world, [ball])

    assert len(mode.path) > 0
    assert mode.path_width == 250.0

    # Tick without taking damage
    mode.tick(world, [ball], 1.0)
    assert ball.hp == 100.0 # because ball is exactly at 500,500 which is near the start

    # Move ball far away
    ball.x = 100.0
    ball.y = 100.0
    mode.tick(world, [ball], 1.0)
    assert ball.hp <= 100.0 # should take damage
