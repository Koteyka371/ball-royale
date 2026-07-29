import pytest
import math
from ai.game_modes import GAME_MODES, SnowballMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockHazard:
    def __init__(self, x, y, radius, kind):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.active = True

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 20.0
        self.mass = 1.0
        self.damage = 10.0
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0

def test_snowball_fight_mode_registered():
    assert "snowball_fight" in GAME_MODES
    assert isinstance(GAME_MODES["snowball_fight"], SnowballMode)

def test_snowball_growth_on_ice():
    world = MockWorld()
    # Add an ice patch
    world.arena.hazards.append(MockHazard(100, 100, 50, "ice_patch"))

    # Fast moving ball on ice
    b1 = MockBall(100, 100, 50.0, 0.0)
    # Slow moving ball on ice
    b2 = MockBall(100, 100, 5.0, 0.0)
    # Fast moving ball off ice
    b3 = MockBall(500, 500, 50.0, 0.0)

    mode = GAME_MODES["snowball_fight"]
    mode.tick(world, [b1, b2, b3], 1.0) # delta=1.0 for pronounced effect

    # b1 should grow (fast and on ice)
    assert b1.radius > 20.0
    assert b1.mass > 1.0
    assert b1.damage > 10.0

    # b2 should not grow (on ice but not moving fast enough)
    assert b2.radius == 20.0
    assert b2.mass == 1.0
    assert b2.damage == 10.0

    # b3 should not grow (fast but off ice)
    assert b3.radius == 20.0
    assert b3.mass == 1.0
    assert b3.damage == 10.0
