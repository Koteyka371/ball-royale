import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, w=1000.0, h=1000.0):
        self.width = w
        self.height = h
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "base"

def test_black_hole_mutator():
    mode = GAME_MODES.get("black_hole_mutator")
    assert mode is not None

    world = MockWorld()
    balls = [MockBall(x=100.0, y=500.0)]

    mode.setup(world, balls)

    bh = next((h for h in world.arena.hazards if getattr(h, "kind", "") == "black_hole"), None)
    assert bh is not None, "Black hole not spawned"
    assert bh.x == 500.0 and bh.y == 500.0

    mode.tick(world, balls, delta=1.0)

    # Ball should be pulled towards center (+x direction)
    assert balls[0].vx > 0.0
    assert balls[0].vy == 0.0

print("Test written!")
