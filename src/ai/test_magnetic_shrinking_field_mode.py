import pytest
from ai.game_modes import MagneticShrinkingFieldMode
from unittest.mock import MagicMock

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.ball_type = "normal"
        self.traits = []

def test_magnetic_shrinking_field_mode_inside():
    mode = MagneticShrinkingFieldMode()
    world = MockWorld()
    b1 = MockBall(1, 500, 500)
    balls = [b1]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    # b1 is inside, should not be pulled or damaged
    assert b1.x == 500
    assert b1.hp == 100.0

def test_magnetic_shrinking_field_mode_outside():
    mode = MagneticShrinkingFieldMode()
    world = MockWorld()
    # Initial bounds are 0 to 1000. Shrink by 10 per sec.
    # We tick by 1 sec -> min_x becomes 10.
    b1 = MockBall(1, 5, 500) # Outside the safe zone (x < 10)
    balls = [b1]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    # The center is 500, 500. Vector from center to b1 is (-495, 0).
    # Normal is (-1, 0). Outward pull strength is 2000 * 1 = 2000.
    # b1.x should become 5 - 2000 = -1995.
    assert b1.x == -1995.0
    assert b1.hp < 100.0 # Takes damage
