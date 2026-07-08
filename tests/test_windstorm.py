import sys
import os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.max_hp = 100
        self.hp = 100
        self.damage = 10
        self.vx = 0.0
        self.vy = 0.0

class MockWorld:
    pass

def test_windstorm_mode():
    mode = GAME_MODES["windstorm"]
    world = MockWorld()
    balls = [MockBall(1), MockBall(2, "scout")]

    mode.setup(world, balls)
    mode.push_timer = 3.0
    mode.push_duration = 0.0
    assert mode.push_timer == 3.0
    assert mode.push_duration == 0.0

    # Fast forward push_timer
    mode.push_timer = 0.0
    mode.tick(world, balls, 0.1)

    # push_duration should now be > 0
    assert mode.push_duration > 0.0

    # Check if push is applied
    assert (balls[0].vx != 0.0 or balls[0].vy != 0.0)
    assert (balls[1].vx != 0.0 or balls[1].vy != 0.0)

    # Balls should have equal applied force for this tick
    assert math.isclose(balls[0].vx, balls[1].vx)
    assert math.isclose(balls[0].vy, balls[1].vy)

def test_windstorm_ignores_spectator():
    mode = GAME_MODES["windstorm"]
    world = MockWorld()
    balls = [MockBall(1, "spectator"), MockBall(2, "scout")]

    mode.setup(world, balls)
    mode.push_timer = 0.0
    mode.push_duration = 0.0
    mode.tick(world, balls, 0.1)

    assert mode.push_duration > 0.0

    # Spectator should not be affected
    assert balls[0].vx == 0.0
    assert balls[0].vy == 0.0

    # Scout should be affected
    assert (balls[1].vx != 0.0 or balls[1].vy != 0.0)

def test_windstorm_ignores_dead():
    mode = GAME_MODES["windstorm"]
    world = MockWorld()
    balls = [MockBall(1, "warrior", False), MockBall(2, "scout")]

    mode.setup(world, balls)
    mode.push_timer = 0.0
    mode.push_duration = 0.0
    mode.tick(world, balls, 0.1)

    assert mode.push_duration > 0.0

    # Dead ball should not be affected
    assert balls[0].vx == 0.0
    assert balls[0].vy == 0.0

    # Scout should be affected
    assert (balls[1].vx != 0.0 or balls[1].vy != 0.0)
