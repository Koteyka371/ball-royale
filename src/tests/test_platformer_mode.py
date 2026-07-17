import pytest
from ai.game_modes import GAME_MODES
from arena.arena_types import ARENAS

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 10000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.killer = ""
        self.traits = []
        self.ball_type = "basic"

def test_platformer_mode():
    assert "platformer" in GAME_MODES
    assert "platformer" in ARENAS

    mode = GAME_MODES["platformer"]
    arena_class = ARENAS["platformer"]
    arena = arena_class()
    arena.generate()

    assert arena.width == 10000.0
    assert len(arena.hazards) > 0

    world = MockWorld()
    ball_safe = MockBall(500, 500)
    ball_fall = MockBall(500, 1100)

    mode.apply_dynamic_traits(world, [ball_safe, ball_fall], 0.1)

    assert ball_safe.alive
    assert not ball_fall.alive
    assert ball_fall.killer == "fall_damage"
