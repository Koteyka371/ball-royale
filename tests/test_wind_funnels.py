import pytest
import math
from ai.game_modes import WindFunnelsMode

class MockArena:
    def __init__(self):
        self.width = 1500.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True

def test_wind_funnels_mode():
    mode = WindFunnelsMode()
    world = MockWorld()
    b1 = MockBall(500, 500)
    b2 = MockBall(10, 10) # far away

    mode.setup(world, [b1, b2])

    assert len(mode.funnels) >= 3
    assert len(world.arena.hazards) >= 3

    # Force a funnel to be right on top of b1
    f = mode.funnels[0]
    f["x1"] = 400
    f["y1"] = 500
    f["x2"] = 600
    f["y2"] = 500
    f["dir_x"] = 1.0
    f["dir_y"] = 0.0
    f["force"] = 1000.0
    f["width"] = 50.0
    f["length_sq"] = 200**2

    mode.tick(world, [b1, b2], 0.1)

    assert b1.vx > 0.0
    assert b1.vy == 0.0
    assert b2.vx == 0.0
    assert b2.vy == 0.0
