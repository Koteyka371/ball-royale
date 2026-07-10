import pytest
import math
from ai.game_modes import GAME_MODES

class MockBooster:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.arena = MockArena()
        self.boosters = []

def test_vortex_orbit_mode():
    mode = GAME_MODES.get("vortex_orbit")
    assert mode is not None

    world = MockWorld()
    world.boosters.append(MockBooster(x=550, y=500)) # right of center by 50

    mode.apply(world, 0.1)

    # cx = 500, cy = 500
    # bx = 550, by = 500
    # dx = -50, dy = 0
    # dist = 50, nx = -1, ny = 0
    # px = 0, py = -1
    # not dist > 200 (pull check skipped)
    # bx += 0, by += -1 * 300 * 0.1 = -30
    # new x = 550, new y = 470

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "vortex"

    b = world.boosters[0]
    assert math.isclose(b.x, 550.0)
    assert math.isclose(b.y, 470.0)
