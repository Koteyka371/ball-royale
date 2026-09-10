import pytest
import math
from ai.game_modes import GameMode, GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.vy = 0.0
        self.alive = True
        self.ball_type = "normal"
        self.traits = []
        self.radius = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_max_speed = 100.0
        self.max_speed = 100.0
        self.hp = 100.0
        self.max_hp = 100.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.gravity_y = 50.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, kind, data):
        self.events.append({"type": kind, **data})

def test_gravity_inverter_setup():
    mode = GAME_MODES["gravity_inverter_hazard"]
    world = MockWorld()
    b1 = MockBall(1, 100, 100)

    mode.setup(world, [b1])

    assert len(world.arena.hazards) > 0
    inverter = world.arena.hazards[0]
    assert getattr(inverter, "kind", "") == "gravity_inverter"
    assert getattr(inverter, "x", 0) == 500.0
    assert getattr(inverter, "y", 0) == 500.0
    assert getattr(inverter, "radius", 0) == 150.0

def test_gravity_inverter_push():
    mode = GAME_MODES["gravity_inverter_hazard"]
    world = MockWorld()
    # Left of center
    b1 = MockBall(1, 400, 500)

    mode.setup(world, [b1])

    orig_x = b1.x
    orig_y = b1.y
    orig_vy = b1.vy

    mode.tick(world, [b1], 1.0)

    # Should be pushed away from center (center is 500)
    # x < 500, so it should be pushed further left
    assert b1.x < orig_x
    assert b1.y == orig_y

    # Gravity inverter effect
    assert b1.vy < orig_vy

def test_gravity_inverter_outside_no_effect():
    mode = GAME_MODES["gravity_inverter_hazard"]
    world = MockWorld()
    b2 = MockBall(2, 100, 100)

    mode.setup(world, [b2])

    orig_x = b2.x
    orig_y = b2.y
    orig_vy = b2.vy

    mode.tick(world, [b2], 1.0)

    assert b2.x == orig_x
    assert b2.y == orig_y
    assert b2.vy == orig_vy
