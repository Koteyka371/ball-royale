import pytest
import math
from game_modes import RotatingLasersMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.weather = "clear"
        self.name = "default"
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.boosters = []
    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.radius = 20.0
        self.alive = True
    def take_damage(self, amount):
        self.hp -= amount

def test_rotating_lasers_setup():
    mode = RotatingLasersMode()
    world = MockWorld()
    mode.setup(world, [])

    assert len(mode.lasers) == 2
    assert mode.lasers[0]["x"] == 500.0
    assert mode.lasers[0]["y"] == 500.0
    assert mode.lasers[0]["angle"] == 0.0
    assert mode.lasers[1]["angle"] == 180.0

def test_rotating_lasers_rotation():
    mode = RotatingLasersMode()
    world = MockWorld()
    mode.setup(world, [])

    # 1 second of rotation at 45 deg/sec
    mode.apply_dynamic_traits(world, [], 1.0)
    assert mode.lasers[0]["angle"] == 45.0
    assert mode.lasers[1]["angle"] == 225.0

def test_rotating_lasers_damage():
    mode = RotatingLasersMode()
    world = MockWorld()
    mode.setup(world, [])

    # we override rotation to not happen during apply_dynamic_traits for this test
    # by applying a negative delta for angle, or just setting angular velocity to 0
    # Wait, we want damage to scale with delta=1.0, so let's set angular_velocity=0
    for l in mode.lasers:
        l["angular_velocity"] = 0.0

    b1 = MockBall(1, 500.0, 500.0)
    b2 = MockBall(2, 500.0, 100.0)
    b3 = MockBall(3, 1000.0, 500.0)

    mode.apply_dynamic_traits(world, [b1, b2, b3], 1.0)

    # b1 is at center, intersects both lasers.
    assert b1.hp == 100.0 - (50.0 * 1.0) * 2

    # b2 is far above, laser is horizontal. Should take no damage.
    assert b2.hp == 100.0

    # b3 is directly on the right, intersecting the first laser.
    assert b3.hp == 100.0 - 50.0 * 1.0
