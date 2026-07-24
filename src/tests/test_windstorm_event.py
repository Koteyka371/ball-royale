import math
import sys
import os
import pytest

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
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_windstorm_event_mode():
    mode = GAME_MODES["windstorm_event"]
    world = MockWorld()
    balls = [MockBall(1), MockBall(2, "scout")]

    mode.setup(world, balls)

    # Fast forward event_timer
    mode.event_timer = 0.0
    mode.tick(world, balls, 0.1)

    assert mode.is_active == True
    assert mode.event_duration == 10.0
    assert len(world.events) > 0

    # Start push
    mode.push_timer = 0.0
    mode.push_duration = 0.0
    mode.tick(world, balls, 0.1)

    assert mode.push_duration > 0.0
    assert (balls[0].vx != 0.0 or balls[0].vy != 0.0)
    assert (balls[1].vx != 0.0 or balls[1].vy != 0.0)
    assert math.isclose(balls[0].vx, balls[1].vx)
    assert math.isclose(balls[0].vy, balls[1].vy)

def test_windstorm_event_ignores_spectator():
    mode = GAME_MODES["windstorm_event"]
    world = MockWorld()
    balls = [MockBall(1, "spectator"), MockBall(2, "scout")]

    mode.setup(world, balls)
    mode.event_timer = 0.0
    mode.tick(world, balls, 0.1) # activate

    mode.push_timer = 0.0
    mode.push_duration = 0.0
    mode.tick(world, balls, 0.1) # start push

    assert mode.push_duration > 0.0

    # Spectator should not be affected
    assert balls[0].vx == 0.0
    assert balls[0].vy == 0.0

    # Scout should be affected
    assert (balls[1].vx != 0.0 or balls[1].vy != 0.0)

def test_windstorm_event_ignores_dead():
    mode = GAME_MODES["windstorm_event"]
    world = MockWorld()
    balls = [MockBall(1, "warrior", False), MockBall(2, "scout")]

    mode.setup(world, balls)
    mode.event_timer = 0.0
    mode.tick(world, balls, 0.1) # activate

    mode.push_timer = 0.0
    mode.push_duration = 0.0
    mode.tick(world, balls, 0.1) # start push

    assert mode.push_duration > 0.0

    # Dead ball should not be affected
    assert balls[0].vx == 0.0
    assert balls[0].vy == 0.0

    # Scout should be affected
    assert (balls[1].vx != 0.0 or balls[1].vy != 0.0)
