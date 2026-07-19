import pytest
import math
from ai.game_modes import GAME_MODES

def test_decreasing_safe_zones_exist():
    assert "decreasing_safe_zones" in GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, id, x, y, hp=100, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.weather_immunity_timer = 0.0
        self.ball_type = "player"

def test_decreasing_safe_zones_mode():
    mode = GAME_MODES["decreasing_safe_zones"]
    world = MockWorld()

    b_inside = MockBall(1, 500, 500)
    b_outside = MockBall(2, -100, -100) # Guarantee outside
    balls = [b_inside, b_outside]

    # Mock randomness so we know where zones are
    mode.setup(world, balls)

    # We will override zones to make sure b_inside is in the zone and b_outside isn't
    mode.zones = [{"x": 500, "y": 500, "radius": 100}]
    mode.num_zones = 5

    # Initially wait for timer
    mode.tick(world, balls, delta=1.0)
    assert b_inside.hp == 100
    assert b_outside.hp == 100
    assert mode.num_zones == 5

    # Fast forward to timer expiring
    mode.tick(world, balls, delta=14.0)
    # Timer should now hit 0, triggering damage
    assert b_inside.hp == 100
    assert b_outside.hp <= 0
    assert not b_outside.alive
    assert b_outside.id in world.dead_balls

    # Setup for next round should have happened
    assert mode.num_zones == 4
    assert len(mode.zones) == 4
    assert mode.round_timer == mode.max_round_timer
