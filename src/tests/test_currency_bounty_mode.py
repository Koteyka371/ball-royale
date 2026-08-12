import pytest
from ai.game_modes import CurrencyBountyMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.currency_pickups = []
        self.events = []
        self.tick = 0

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

class MockBall:
    def __init__(self, ball_id, x, y, alive=True):
        self.id = ball_id
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = "player"
        self.speed = 100.0
        self.damage = 10.0
        self.radius = 15.0
        self.vx = 0.0
        self.vy = 0.0
        self.currency = 0

def test_currency_bounty_mode():
    mode = CurrencyBountyMode()
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 500, 500)
    balls = [b1, b2]

    mode.setup(world, balls)

    # After setup, get the real base_speed (it could be 120 due to setup base logic, but let's check it dynamically)
    b2_base_speed = getattr(b2, "base_speed", getattr(b2, "speed", 100.0))
    b2_base_damage = getattr(b2, "base_damage", getattr(b2, "damage", 10.0))

    # Give b1 10 currency by placing pickups on top of it
    for i in range(10):
        world.currency_pickups.append({"x": 100, "y": 100, "type": "currency"})

    # Setup b2 to move towards b1
    b2.vx = -1.0
    b2.vy = -1.0

    mode.tick(world, balls, 0.016)

    # Check that b1 collected the currency
    assert getattr(b1, "currency", 0) >= 10

    # Since b1 is the bounty target and b2 is moving towards b1, b2 should have bonus stats
    assert b2.speed > b2_base_speed
    assert b2.damage > b2_base_damage

    # Events should have a bounty compass
    assert any(e["type"] == "bounty_compass" and e["data"]["owner_id"] == 1 for e in world.events)

    # Move b2 away from b1
    b2.vx = 1.0
    b2.vy = 1.0
    mode.tick(world, balls, 0.016)

    # b2 should no longer have bonus stats
    assert b2.speed == b2_base_speed
    assert b2.damage == b2_base_damage
