import pytest
from src.ai.game_modes import BlackHoleMutatorMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "normal"

def test_black_hole_mutator_setup():
    mode = BlackHoleMutatorMode()
    world = MockWorld()

    mode.setup(world, [])

    assert len(world.arena.hazards) == 1
    bh = world.arena.hazards[0]
    assert getattr(bh, "kind") == "massive_black_hole"
    assert getattr(bh, "x") == 500.0
    assert getattr(bh, "y") == 500.0
    assert getattr(bh, "radius") == 80.0

def test_black_hole_mutator_tick():
    mode = BlackHoleMutatorMode()
    world = MockWorld()
    mode.setup(world, [])

    # Ball near center
    b1 = MockBall(400.0, 500.0)
    # Ball far from center
    b2 = MockBall(10.0, 10.0)

    mode.tick(world, [b1, b2], delta=1.0)

    # Both should be pulled towards center (500, 500)
    assert b1.vx > 0.0  # Pulled right
    assert b2.vx > 0.0  # Pulled right
    assert b2.vy > 0.0  # Pulled down

    # Near ball takes more damage than far ball
    damage_b1 = 100.0 - b1.hp
    damage_b2 = 100.0 - b2.hp
    assert damage_b1 > damage_b2
    assert damage_b1 > 0.0
