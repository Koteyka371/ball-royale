import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.id = "p1"

class MockWorld:
    pass

def test_reversed_input_mode():
    mode = GAME_MODES["reversed_input"]
    assert mode.name == "Reversed Input"

    world = MockWorld()

    # Simulate a ball that has just moved based on its velocity
    # e.g. started at (10, 10) with vx=100, vy=0
    # delta = 0.1s -> dx = 10 -> current pos = (20, 10)
    ball = MockBall(20.0, 10.0, 100.0, 0.0)
    balls = [ball]

    # Tick mode
    mode.tick(world, balls, delta=0.1)

    # Ball should have moved back 2 * dx = 20, ending at x = 0
    # Equivalent to moving from 10 to 0 instead of 10 to 20.
    assert ball.x == 0.0
    assert ball.y == 10.0
