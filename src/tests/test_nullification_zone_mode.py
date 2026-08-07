import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

def test_nullification_zone_mode():
    mode = GAME_MODES.get("nullification_zone")
    assert mode is not None

    world = MagicMock()
    arena = MagicMock()
    arena.width = 1000.0
    arena.height = 1000.0
    arena.hazards = []
    arena.is_raining = False

    world.arena = arena
    world.dead_balls = []
    world.boosters = []
    world.lightning_strike_timer = 0.0
    world.weekly_mutator = ''

    lm = MagicMock()
    lm.data = {'current_season': 1}
    world.leaderboard_manager = lm

    pm = MagicMock()
    pm.leaderboard_manager = lm
    pm.data = {}
    world.profile_manager = pm

    ball_in = MagicMock()
    ball_in.alive = True
    ball_in.x = 500.0
    ball_in.y = 500.0
    ball_in.stamina = 100.0
    ball_in.silence_timer = 0.0
    ball_in.weather_immunity_timer = 0.0
    ball_in.hp = 100.0
    ball_in.max_hp = 100.0
    ball_in.traits = []
    ball_in.badges = []

    ball_out = MagicMock()
    ball_out.alive = True
    ball_out.x = 100.0
    ball_out.y = 100.0
    ball_out.stamina = 100.0
    ball_out.silence_timer = 0.0
    ball_out.weather_immunity_timer = 0.0
    ball_out.hp = 100.0
    ball_out.max_hp = 100.0
    ball_out.traits = []
    ball_out.badges = []

    balls = [ball_in, ball_out]

    mode.setup(world, balls)

    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0
    assert len(arena.hazards) == 1
    assert arena.hazards[0].kind == "nullification_zone"

    mode.tick(world, balls, delta=1.0)

    # ball_in should have drained stamina and silence_timer applied
    assert ball_in.stamina == 85.0
    assert ball_in.silence_timer == 0.5

    # ball_out should be unaffected
    assert ball_out.stamina == 100.0
    assert ball_out.silence_timer == 0.0
