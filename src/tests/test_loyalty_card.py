import pytest
from unittest.mock import MagicMock
from ai.game_modes import BlackMarketMode

class MockBall:
    def __init__(self, id, ball_type="basic"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.currency = 0
        self.purchase_cooldown = 0.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.speed = 100.0
        self.damage = 10.0

def _setup_world():
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    if hasattr(world, "leaderboard_manager"):
        del world.leaderboard_manager
    if hasattr(world, "profile_manager"):
        del world.profile_manager
    return world

def test_loyalty_card_purchase():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = []
    world.black_markets = [{"x": 100.0, "y": 100.0, "vx": 0.0, "vy": 0.0, "radius": 40.0}]

    ball = MockBall(1)
    ball.x = 100.0
    ball.y = 100.0
    ball.currency = 15
    ball.purchase_cooldown = 0.0

    balls = [ball]

    mode.tick(world, balls, 0.016)

    assert getattr(ball, "has_loyalty_card", False) == True
    assert ball.currency == 0
    assert ball.purchase_cooldown > 0.0

def test_loyalty_card_discount():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = []
    world.black_markets = [{"x": 100.0, "y": 100.0, "vx": 0.0, "vy": 0.0, "radius": 40.0}]

    ball = MockBall(1)
    ball.x = 100.0
    ball.y = 100.0
    ball.currency = 4
    ball.has_loyalty_card = True
    ball.purchase_cooldown = 0.0

    balls = [ball]

    mode.tick(world, balls, 0.016)

    assert getattr(ball, "has_loyalty_card", False) == True
    assert ball.currency == 0
    assert ball.purchase_cooldown > 0.0
