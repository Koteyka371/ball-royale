import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.game_modes import BlackoutMode

class MockBall:
    def __init__(self, ball_type="basic", alive=True):
        self.ball_type = ball_type
        self.alive = alive
        self.perception_radius = 250.0

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_blackout_mode_setup():
    mode = BlackoutMode()
    world = MockWorld()
    balls = [MockBall(), MockBall("spectator"), MockBall()]

    mode.setup(world, balls)

    assert getattr(balls[0], "base_perception_radius", 250.0) == 250.0
    assert balls[0].team == "basic"
    assert not hasattr(balls[1], "base_perception_radius")  # Spectator untouched

def test_blackout_mode_tick():
    mode = BlackoutMode()
    world = MockWorld()
    balls = [MockBall()]
    mode.setup(world, balls)

    # Tick below 5.0s (no change)
    mode.tick(world, balls, 4.0)
    assert not mode.is_blackout
    assert balls[0].perception_radius == 250.0

    # Tick above 5.0s (blackout triggers)
    mode.tick(world, balls, 1.1)
    assert mode.is_blackout
    assert balls[0].perception_radius == 50.0
    assert len(world.events) == 1
    assert world.events[0][0] == "weather_warning"

    # Tick above 5.0s again (blackout ends)
    mode.tick(world, balls, 5.1)
    assert not mode.is_blackout
    assert balls[0].perception_radius == 250.0
    assert len(world.events) == 2
