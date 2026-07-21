import pytest
from unittest.mock import MagicMock
from ai.game_modes import BattleRoyaleMode

def test_acid_rain_dot_application():
    mode = BattleRoyaleMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.arena.width = 1000.0
    world.arena.height = 1000.0

    b1 = MagicMock()
    b1.alive = True
    b1.ball_type = "knight"
    b1.x, b1.y = 500.0, 500.0
    b1.hp = 100.0
    b1.weather_immunity_timer = 0.0
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    del b1.take_damage
    b1.shielding = 0.0
    b1.hazmat_booster_timer = 0.0
    b1.weather_control_timer = 0.0
    b1.vision_booster_timer = 0.0
    b1.burn_timer = 0.0
    b1.kinetic_shield_active = False
    b1.mega_hazmat_booster_timer = 0.0
    b1.umbrella_booster_timer = 0.0

    b2 = MagicMock()
    b2.alive = True
    b2.ball_type = "knight"
    b2.x, b2.y = 500.0, 500.0
    b2.hp = 100.0
    b2.weather_immunity_timer = 0.0
    del b2.take_damage
    b2.shielding = 50.0
    b2.hazmat_booster_timer = 0.0
    b2.weather_control_timer = 0.0
    b2.vision_booster_timer = 0.0
    b2.burn_timer = 0.0
    b2.kinetic_shield_active = False
    b2.mega_hazmat_booster_timer = 0.0
    b2.umbrella_booster_timer = 0.0

    mode.setup(world, [b1, b2])

    # Tick to activate acid rain
    mode.acid_rain_timer = 45.0
    mode.tick(world, [b1, b2], delta=0.2)

    b1.hp = 100.0
    b2.hp = 100.0

    # Tick for 1 second during acid rain
    mode.tick(world, [b1, b2], delta=1.0)

    # Unshielded ball should take damage (10.0 * 1.0)
    assert b1.hp == 90.0

    # Shielded ball should not take damage
    assert b2.hp == 100.0
