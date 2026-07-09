import math
import random
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
    world.add_event = MagicMock()
    return world

def test_gambling_node_win():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = []
    world.black_markets = []
    world.gambling_nodes = [{"x": 100.0, "y": 100.0, "radius": 40.0}]

    ball = MockBall(1)
    ball.x = 100.0
    ball.y = 100.0
    ball.currency = 5
    ball.purchase_cooldown = 0.0

    balls = [ball]

    random.seed(42) # Try to predict roll
    # we need to make sure we force the random roll to < 0.333
    with pytest.MonkeyPatch().context() as m:
        m.setattr(random, 'randint', lambda a,b: 5)
        m.setattr(random, 'random', lambda: 0.1)
        mode.tick(world, balls, 0.016)

    assert ball.currency == 10
    assert ball.purchase_cooldown == 5.0
    world.add_event.assert_called_with("gambling_win", {"ball": ball, "amount": 10})

def test_gambling_node_lose():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = []
    world.black_markets = []
    world.gambling_nodes = [{"x": 100.0, "y": 100.0, "radius": 40.0}]

    ball = MockBall(1)
    ball.x = 100.0
    ball.y = 100.0
    ball.currency = 5
    ball.purchase_cooldown = 0.0

    balls = [ball]

    with pytest.MonkeyPatch().context() as m:
        m.setattr(random, 'randint', lambda a,b: 5)
        m.setattr(random, 'random', lambda: 0.5)
        mode.tick(world, balls, 0.016)

    assert ball.currency == 0
    assert ball.purchase_cooldown == 5.0
    world.add_event.assert_called_with("gambling_lose", {"ball": ball, "amount": 5})

def test_gambling_node_explode():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = []
    world.black_markets = []
    world.gambling_nodes = [{"x": 100.0, "y": 100.0, "radius": 40.0}]

    ball = MockBall(1)
    ball.x = 100.0
    ball.y = 100.0
    ball.currency = 5
    ball.purchase_cooldown = 0.0

    ball2 = MockBall(2)
    ball2.x = 120.0
    ball2.y = 120.0

    ball3 = MockBall(3)
    ball3.x = 500.0
    ball3.y = 500.0

    balls = [ball, ball2, ball3]

    with pytest.MonkeyPatch().context() as m:
        m.setattr(random, 'randint', lambda a,b: 5)
        m.setattr(random, 'random', lambda: 0.9)
        mode.tick(world, balls, 0.016)

    assert ball.currency == 0
    assert ball.purchase_cooldown == 5.0
    assert ball.hp == 50.0
    assert ball2.hp == 50.0
    assert ball3.hp == 100.0
