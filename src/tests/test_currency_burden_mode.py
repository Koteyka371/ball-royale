import pytest
import math
from unittest.mock import MagicMock
import random
from ai.game_modes import CurrencyBurdenMode

class MockBall:
    def __init__(self, id, ball_type="basic"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.currency = 0
        self.max_hp = 100.0
        self.hp = 100.0
        self.speed = 100.0
        self.damage = 10.0

def _setup_world():
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.add_event = MagicMock()

    # Actually just set these to lists
    world.currency_pickups = []
    world.altars = []
    world.boosters = []

    if hasattr(world, "leaderboard_manager"):
        del world.leaderboard_manager
    if hasattr(world, "profile_manager"):
        del world.profile_manager
    return world

def test_currency_burden_setup():
    mode = CurrencyBurdenMode()
    world = _setup_world()
    balls = [MockBall(1)]
    mode.setup(world, balls)

    assert hasattr(world, "currency_pickups")
    assert len(world.currency_pickups) >= 15
    assert hasattr(world, "altars")
    assert len(world.altars) == 3
    assert getattr(world, "boosters", []) == []

def test_currency_burden_tick_collect():
    mode = CurrencyBurdenMode()
    world = _setup_world()
    ball = MockBall(1)
    ball.x = 50.0
    ball.y = 50.0
    ball.speed = 100.0
    ball.damage = 10.0
    balls = [ball]

    world.currency_pickups = [{"x": 55.0, "y": 55.0, "type": "currency"}]
    world.altars = []

    mode.tick(world, balls, 0.016)

    assert ball.currency == 1
    assert len(world.currency_pickups) == 0
    # Slower speed
    assert ball.speed < ball.base_speed
    # Higher damage
    assert ball.damage > ball.base_damage
    # Larger radius
    assert ball.radius > ball.base_radius

def test_currency_burden_tick_altar():
    mode = CurrencyBurdenMode()
    world = _setup_world()
    ball = MockBall(1)
    ball.x = 100.0
    ball.y = 100.0
    ball.currency = 10
    ball.speed = 100.0
    ball.damage = 10.0
    balls = [ball]

    world.currency_pickups = []
    world.altars = [{"x": 100.0, "y": 100.0, "radius": 50.0}]

    # We mock random choice to always pick base_speed upgrade
    with pytest.MonkeyPatch().context() as m:
        m.setattr(random, "choice", lambda x: "base_speed")
        mode.tick(world, balls, 0.016)

    # Deposited all currency
    assert ball.currency == 0
    assert ball.base_speed == 120.0 # 100 + 2.0 * 10
    # Speed reset to new base speed without debuff
    assert ball.speed == 120.0

    world.add_event.assert_called_once()
