import pytest

class MockArena:
    def __init__(self):
        self.boundary_offsets = {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000.0
        self.height = 1000.0

class MockBall:
    def __init__(self, id, x, y, hp):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True

def test_crumbling_arena_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES.get("crumbling_arena")
    assert mode is not None

    world = MockWorld()

    ball1 = MockBall(1, 100.0, 100.0, 100.0)

    balls = [ball1]

    mode.setup(world, balls)

    ball1.hp -= 20.0

    mode.tick(world, balls, 0.016)

    offsets = world.arena.boundary_offsets
    assert offsets["top"] > 0.0 or offsets["left"] > 0.0

    assert len(world.arena.hazards) > 0
