import math
import pytest
from ai.game_modes import GAME_MODES

def test_multiple_safe_zones_exist():
    assert "multiple_safe_zones" in GAME_MODES


class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, x, y, hp=100, alive=True):
        self.id = 1
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.weather_immunity_timer = 0.0

def test_multiple_safe_zones_mode():
    mode = GAME_MODES["multiple_safe_zones"]
    world = MockWorld()

    b_inside = MockBall(500, 500)
    b_outside = MockBall(100, 100)

    balls = [b_inside, b_outside]

    mode.setup(world, balls)

    assert len(mode.zones) == 1
    assert mode.zones[0]["x"] == 500.0
    assert mode.zones[0]["y"] == 500.0

    # Test tick (outside takes damage)
    mode.tick(world, balls, 1.0)
    assert b_inside.hp == 100
    assert b_outside.hp < 100

    # Test split
    mode.split_timer = 0.0
    mode.tick(world, balls, 1.0)

    # Initial radius 500. After split, it should be 2.
    assert len(mode.zones) == 2
    # Radius of each new zone should be smaller
    assert mode.zones[0]["radius"] < 500.0
    assert mode.zones[1]["radius"] < 500.0
