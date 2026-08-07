import pytest
import sys
sys.path.insert(0, "src")

from ai.game_modes import CrumblingArenaMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000.0
        self.height = 1000.0

class MockBall:
    def __init__(self, id, x, y, hp, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.team = "A"

def test_crumbling_arena():
    mode = CrumblingArenaMode()
    world = MockWorld()
    b1 = MockBall(1, 50, 50, 100) # near top/left wall

    mode.setup(world, [b1])

    assert world.arena.boundary_offsets == {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}

    # take damage
    b1.hp = 80

    mode.tick(world, [b1], 0.016)

    assert world.arena.boundary_offsets["top"] > 0 or world.arena.boundary_offsets["left"] > 0
    assert len(world.arena.hazards) > 0

if __name__ == "__main__":
    test_crumbling_arena()
    print("Test passed!")
