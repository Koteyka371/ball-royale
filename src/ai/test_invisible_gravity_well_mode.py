import pytest
from ai.game_modes import GAME_MODES, InvisibleGravityWellsMode

class MockArena:
    def __init__(self):
        self.width = 2000
        self.height = 2000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "normal"

def test_invisible_gravity_wells_mode():
    mode = GAME_MODES["invisible_gravity_wells"]
    world = MockWorld()
    b = MockBall(500, 500)
    balls = [b]

    mode.setup(world, balls)

    # Force spawn a well at 600, 500
    mode.wells.append({"x": 600, "y": 500, "radius": 200, "duration": 5.0, "pull": 150.0})

    mode.apply_dynamic_traits(world, balls, 0.1)

    # Ball should have its velocity altered towards 600 on the x axis
    assert b.vx > 0.0

def test_invisible_gravity_wells_mode_spawns_wells():
    mode = GAME_MODES["invisible_gravity_wells"]
    world = MockWorld()
    b = MockBall(500, 500)
    balls = [b]

    mode.setup(world, balls)

    mode.apply_dynamic_traits(world, balls, 4.1) # Exceed spawn timer

    assert len(mode.wells) == 1
