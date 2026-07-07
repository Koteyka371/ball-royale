import pytest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, alive=True, ball_type="player"):
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type
        self.hp = 100

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_sweeping_black_hole_mode():
    mode = GAME_MODES.get("sweeping_black_hole")
    assert mode is not None, "SweepingBlackHoleMode not implemented yet"

    world = MockWorld()
    balls = [MockBall(500, 500)]
    mode.setup(world, balls)

    # Initial state should be false
    assert mode.is_sweeping is False

    # Tick should spawn the black hole and move it
    mode.tick(world, balls, delta=1.0)

    assert mode.is_sweeping is True
    # It should have moved from its spawn point

    # We tick enough times to test movement and interaction
    for _ in range(10):
        mode.tick(world, balls, delta=1.0)

    # The ball is at 500,500. Depending on where the black hole spawned,
    # the ball should have been pulled from 500,500
    b = balls[0]
    assert b.x != 500 or b.y != 500, "Ball should have been pulled by the black hole"

    # Make ball overlap with black hole directly to test death
    b.x = mode.bh_x
    b.y = mode.bh_y
    mode.tick(world, balls, delta=1.0)

    assert b.alive is False
    assert b.hp == 0
