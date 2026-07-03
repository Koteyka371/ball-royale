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

def test_black_market_setup():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = []
    world.black_markets = []
    balls = [MockBall(1), MockBall(2)]

    mode.setup(world, balls)

    assert len(world.currency_pickups) == 15
    assert len(world.black_markets) == 2
    for b in balls:
        assert b.currency == 0
        assert b.purchase_cooldown == 0.0

def test_currency_collection():
    mode = BlackMarketMode()
    world = _setup_world()

    ball = MockBall(1)
    ball.x = 50.0
    ball.y = 50.0
    ball.currency = 0

    world.currency_pickups = [{"x": 55.0, "y": 55.0, "type": "currency"}]
    world.black_markets = []
    balls = [ball]

    mode.setup(world, balls)
    mode.tick(world, balls, 0.016)

    assert ball.currency > 0
    assert len(world.currency_pickups) == 15  # Because setup spawns 15, we check they get removed

def test_currency_collection_precise():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = [{"x": 55.0, "y": 55.0, "type": "currency"}]
    world.black_markets = []

    ball = MockBall(1)
    ball.x = 50.0
    ball.y = 50.0
    ball.currency = 0

    balls = [ball]

    # Setup normally adds 15 pickups, let's bypass it for precision
    mode.tick(world, balls, 0.016)

    # Ball collected the pickup
    assert ball.currency > 0
    assert len(world.currency_pickups) == 0

def test_upgrade_purchase():
    mode = BlackMarketMode()
    world = _setup_world()
    world.currency_pickups = []
    world.black_markets = [{"x": 100.0, "y": 100.0, "vx": 0.0, "vy": 0.0, "radius": 40.0}]

    ball = MockBall(1)
    ball.x = 100.0
    ball.y = 100.0
    ball.currency = 5  # Enough to purchase
    ball.purchase_cooldown = 0.0

    balls = [ball]

    mode.tick(world, balls, 0.016)

    assert ball.currency == 0
    assert ball.purchase_cooldown > 0.0

    # Assert stats went up (random choice, so at least one increased)
    assert ball.max_hp > 100.0 or ball.speed > 100.0 or ball.damage > 10.0
