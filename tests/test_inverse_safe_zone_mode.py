import pytest
from ai.game_modes import InverseSafeZoneMode

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, bid, x, y, hp=100.0, team="Team A"):
        self.id = bid
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.team = team
        self.ball_type = "warrior"
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0

def test_inverse_safe_zone_setup():
    world = MockWorld()
    balls = [MockBall(1, 100, 100), MockBall(2, 900, 900)]
    mode = InverseSafeZoneMode()
    mode.setup(world, balls)

    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0
    assert mode.danger_radius == 50.0
    assert mode.max_danger_radius == 500.0

def test_inverse_safe_zone_tick_damage():
    world = MockWorld()
    # Ball 1 inside danger zone (center is 500,500. rad=50)
    b1 = MockBall(1, 500, 500)
    # Ball 2 outside danger zone
    b2 = MockBall(2, 100, 100)

    balls = [b1, b2]
    mode = InverseSafeZoneMode()
    mode.setup(world, balls)

    initial_hp_b1 = b1.hp
    initial_hp_b2 = b2.hp

    # Tick with delta=1.0
    mode.tick(world, balls, delta=1.0)

    assert mode.danger_radius == 50.0 + 15.0 # expanded
    assert b1.hp == initial_hp_b1 - 20.0
    assert b2.hp == initial_hp_b2 # no damage

def test_inverse_safe_zone_gravitational_push():
    world = MockWorld()
    # Ball near center but not exactly on it to avoid dist=0 issue
    b1 = MockBall(1, 510, 500)

    balls = [b1]
    mode = InverseSafeZoneMode()
    mode.setup(world, balls)

    mode.tick(world, balls, delta=1.0)

    # Should be pushed in positive X direction
    assert b1.vx > 0.0
    assert b1.vy == 0.0
