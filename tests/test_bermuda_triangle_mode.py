import pytest
import math
from ai.game_modes import GAME_MODES, BermudaTriangleMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = 10.0
        self.alive = True
        self.ball_type = "base"

def test_bermuda_triangle_setup_and_tick():
    mode = GAME_MODES.get("bermuda_triangle")
    assert isinstance(mode, BermudaTriangleMode)

    world = MockWorld()
    balls = [MockBall("b1", 500.0, 500.0), MockBall("b2", 10.0, 10.0)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 3
    assert len(mode.pylons) == 3

    # Tick
    mode.tick(world, balls, 0.016)

    # b1 is at center, should teleport and momentum reset
    assert balls[0].vx == 0.0
    assert balls[0].vy == 0.0
    # ensure it's within bounds
    assert 50.0 <= balls[0].x <= 950.0
    assert 50.0 <= balls[0].y <= 950.0

    # b2 is outside, shouldn't teleport
    assert balls[1].vx == 10.0
    assert balls[1].vy == 10.0
    assert balls[1].x == 10.0
    assert balls[1].y == 10.0
