import pytest
import math
from src.ai.game_modes import ShrinkingPinballMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []

class MockEntity:
    def __init__(self, x, y, vx, vy, radius=10.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alive = True
        self.hp = 100.0
        self.bounces = 0

def test_shrinking_pinball_arena_shrinks():
    mode = ShrinkingPinballMode()
    world = MockWorld()
    balls = []
    mode.setup(world, balls)

    assert world.arena.width == 1000.0
    assert world.arena.height == 1000.0

    mode.tick(world, balls, delta=1.0)

    assert world.arena.width == 1000.0 - 15.0
    assert world.arena.height == 1000.0 - 15.0

def test_shrinking_pinball_bounce_multiplier():
    mode = ShrinkingPinballMode()
    world = MockWorld()

    # Entity exactly on left wall going left
    ent = MockEntity(0.0, 500.0, -100.0, 0.0)
    balls = [ent]

    mode.setup(world, balls)

    # Tick for 0 seconds just to process bounce
    mode.tick(world, balls, delta=0.0)

    # Area = 1000x1000 (progress = 0)
    # multiplier = 1.5 + (1.5 * 0) = 1.5
    # new vx = -(-100.0) * 1.5 = 150.0

    assert ent.x == ent.radius
    assert ent.vx == 150.0
    assert ent.bounces == 1

def test_shrinking_pinball_dynamic_multiplier():
    mode = ShrinkingPinballMode()
    world = MockWorld()

    # Simulate an already shrunk arena
    world.arena.width = 500.0
    world.arena.height = 500.0

    ent = MockEntity(500.0, 500.0, 100.0, 0.0)
    balls = [ent]

    mode.setup(world, balls) # captures initial as 500x500
    # Override initial for test
    mode.initial_width = 1000.0
    mode.initial_height = 1000.0

    # Shrink a tiny bit
    mode.tick(world, balls, delta=0.0)

    # Init area = 1M
    # Curr area = 250k
    # progress = 1.0 - (0.25) = 0.75
    # mult = 1.5 + (1.5 * 0.75) = 1.5 + 1.125 = 2.625
    # new vx = -100.0 * 2.625 = -262.5

    assert ent.vx == pytest.approx(-262.5)

def test_shrinking_pinball_with_dict():
    mode = ShrinkingPinballMode()
    world = MockWorld()

    class MockDict(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        def __getattr__(self, key):
            if key in self: return self[key]
            raise AttributeError(key)
        def __setattr__(self, key, value):
            self[key] = value

    ent_dict = MockDict({
        "x": 0.0,
        "y": 500.0,
        "vx": -100.0,
        "vy": 0.0,
        "radius": 10.0,
        "alive": True,
        "hp": 100.0,
        "bounces": 0
    })

    balls = [ent_dict]
    mode.setup(world, balls)
    mode.tick(world, balls, delta=0.0)

    assert ent_dict["x"] == ent_dict["radius"]
    assert ent_dict["vx"] == 150.0
    assert ent_dict["bounces"] == 1
