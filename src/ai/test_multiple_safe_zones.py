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

    balls = []
    mode.setup(world, balls)

    assert len(mode.zones) >= 3

    initial_radius = mode.zones[0]["radius"]

    # Test collapse
    mode.tick(world, balls, 1.0)
    assert mode.zones[0]["radius"] < initial_radius

    # Spawn timer should decrease
    mode.spawn_timer = 0.0
    mode.tick(world, balls, 1.0)

    assert len(mode.zones) >= 4

    # Manually collapse one
    mode.zones[0]["radius"] = -10.0

    b_inside = MockBall(mode.zones[1]["x"], mode.zones[1]["y"])
    b_outside = MockBall(-1000, -1000)
    balls = [b_inside, b_outside]

    mode.tick(world, balls, 1.0)

    assert len(mode.zones) >= 3
    assert b_inside.hp == 100
    assert b_outside.hp < 100
