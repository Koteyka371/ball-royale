import pytest
import math
from ai.game_modes import GameMode, GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
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

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, kind, data):
        self.events.append({"type": kind, **data})

def test_gravity_vortex_setup():
    mode = GAME_MODES["gravity_vortex_hazard"]
    world = MockWorld()
    b1 = MockBall(1, 100, 100)

    mode.setup(world, [b1])

    assert len(world.arena.hazards) > 0
    vortex = world.arena.hazards[0]
    assert getattr(vortex, "kind", "") == "gravity_vortex"
    assert getattr(vortex, "x", 0) == 500.0
    assert getattr(vortex, "y", 0) == 500.0
    assert getattr(vortex, "radius", 0) == 150.0

def test_gravity_vortex_pull_and_slow():
    mode = GAME_MODES["gravity_vortex_hazard"]
    world = MockWorld()
    b1 = MockBall(1, 400, 500)

    mode.setup(world, [b1])

    orig_x = b1.x
    orig_y = b1.y
    orig_speed = getattr(b1, "base_speed", 100.0)

    mode.tick(world, [b1], 1.0)

    assert b1.x > orig_x
    assert b1.y == orig_y
    assert b1.speed < orig_speed
    assert b1.max_speed < orig_speed

def test_gravity_vortex_outside_no_effect():
    mode = GAME_MODES["gravity_vortex_hazard"]
    world = MockWorld()
    b2 = MockBall(2, 100, 100)

    mode.setup(world, [b2])

    orig_x = b2.x
    orig_y = b2.y
    orig_speed = getattr(b2, "base_speed", 100.0)
    orig_max_speed = getattr(b2, "base_max_speed", 100.0)

    # We should update orig_speed/orig_max_speed since GameMode.setup might change base values globally,
    # so we should capture after setup.
    # Actually mode.setup may have mutated base_max_speed depending on global traits,
    # let's just capture the values post-setup before tick.
    post_setup_x = b2.x
    post_setup_y = b2.y
    post_setup_speed = b2.speed
    post_setup_max_speed = b2.max_speed

    mode.tick(world, [b2], 1.0)

    assert b2.x == post_setup_x
    assert b2.y == post_setup_y
    # In gravity vortex hazard, if it's outside the hazard it resets to base_speed and base_max_speed.
    # If mode.setup changes b2.base_speed we should check b2.speed against that base_speed.
    # In MockBall it's explicitly set to 100.0 so we use b2.base_speed.

    assert b2.speed == b2.base_speed
    assert b2.max_speed == b2.base_max_speed
