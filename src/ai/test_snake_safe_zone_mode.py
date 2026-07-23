import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import SnakeSafeZoneMode, GAME_MODES

def test_snake_safe_zone_mode_initialization():
    mode = SnakeSafeZoneMode()
    assert mode.name == "Snake Safe Zone"
    assert "winding, snake-like path" in mode.description

def test_snake_safe_zone_mode_tick():
    mode = SnakeSafeZoneMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.width = 1000
    world.arena.height = 1000
    world.dead_balls = []
    del world.profile_manager
    del world.leaderboard_manager

    ball = MagicMock()
    ball.alive = True
    ball.x = 500
    ball.y = 500
    ball.weather_immunity_timer = 0.0

    balls = [ball]

    mode.setup(world, balls)
    assert len(mode.path_points) == 10

    # Move ball far away to take damage
    ball.x = -1000
    ball.y = -1000

    mode.tick(world, balls, delta=1.0)

    ball.take_damage.assert_called_once()
    world.add_event.assert_called()

def test_snake_safe_zone_mode_registered():
    assert "snake_safe_zone" in GAME_MODES
    assert isinstance(GAME_MODES["snake_safe_zone"], SnakeSafeZoneMode)
