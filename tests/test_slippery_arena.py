import pytest
from ai.game_modes import SlipperyArenaMode

class MockArena:
    def __init__(self):
        self.base_friction = 1.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self):
        self.alive = True
        self.friction_multiplier = 1.0

def test_slippery_arena_friction():
    mode = SlipperyArenaMode()
    w = MockWorld()
    b = MockBall()

    mode.tick(w, [b], 0.016)

    assert w.arena.base_friction == 0.1
    assert b.friction_multiplier == 0.1
