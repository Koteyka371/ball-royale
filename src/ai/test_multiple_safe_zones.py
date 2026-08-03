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

    # Move balls so they are likely inside / outside dynamically generated zones.
    # We will manually set zones after setup to guarantee this test passes properly
    b_inside = MockBall(500, 500)
    b_outside = MockBall(10, 10)

    balls = [b_inside, b_outside]

    mode.setup(world, balls)

    # Should create 3 or 4 zones initially
    assert len(mode.zones) in [3, 4]
    initial_zone_count = len(mode.zones)

    # Overwrite one zone to strictly contain b_inside but not b_outside for damage test
    mode.zones[0]["x"] = 500.0
    mode.zones[0]["y"] = 500.0
    mode.zones[0]["radius"] = 100.0
    for z in mode.zones[1:]:
        z["x"] = 900.0
        z["y"] = 900.0
        z["radius"] = 50.0

    # Test tick (outside takes damage)
    mode.tick(world, balls, 1.0)
    assert b_inside.hp == 100
    assert b_outside.hp < 100

    # Test merge
    mode.merge_timer = 0.0
    mode.tick(world, balls, 1.0)

    # After merge, the number of zones should decrease by 1
    assert len(mode.zones) == initial_zone_count - 1
