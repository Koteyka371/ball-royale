import pytest
from unittest.mock import MagicMock
from ai.game_modes import HealerFreezeTagMode

def create_mock_ball(team):
    b = MagicMock()
    b.ball_type = "normal"
    b.team = team
    b.alive = True
    b.is_frozen = False
    b.is_healer = False
    b.max_stamina = 100.0
    b.stamina = 100.0
    b.base_speed = 100.0
    b.speed = 100.0
    b.base_damage = 10.0
    b.original_base_damage = 10.0
    b.traits = []
    b.weather_immunity_timer = 0.0
    b.in_mirror_dimension = False
    b.intangible = False
    b.vision_radius = 200.0
    b.invisible = False
    b.speed_multiplier = 1.0
    b.stun_timer = 0.0
    b.frozen_timer = 0.0
    b.vx = 0.0
    b.vy = 0.0
    b.x = 0.0
    b.y = 0.0
    b.radius = 15.0
    return b

def test_healer_freeze_tag_setup():
    mode = HealerFreezeTagMode()
    world = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1
    world.arena.hazards = []

    balls = [
        create_mock_ball("Red"), create_mock_ball("Red"),
        create_mock_ball("Blue"), create_mock_ball("Blue")
    ]
    mode.setup(world, balls)

    red_healers = [b for b in balls if b.team == "Red" and getattr(b, "is_healer", False)]
    blue_healers = [b for b in balls if b.team == "Blue" and getattr(b, "is_healer", False)]

    assert len(red_healers) == 1
    assert len(blue_healers) == 1

    assert red_healers[0].is_frozen == False
    assert blue_healers[0].is_frozen == False

    for b in balls:
        if not getattr(b, "is_healer", False):
            assert b.is_frozen == True

    assert len(world.arena.hazards) >= 5
