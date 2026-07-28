import pytest
from ai.game_modes import VisionReducedMode

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

class MockBall:
    def __init__(self, ball_type):
        self.ball_type = ball_type
        self.alive = True
        self.perception_radius = 250.0
        self.team = "player"

def test_vision_reduced_mode():
    mode = VisionReducedMode()
    world = MockWorld()
    ball1 = MockBall("player")
    balls = [ball1]

    mode.setup(world, balls)
    assert ball1.perception_radius == 50.0

    # Tick below pulse active time
    mode.pulse_timer = 2.9
    mode.tick(world, balls, delta=0.05)
    assert abs(mode.pulse_timer - 2.95) < 0.001
    assert ball1.perception_radius == 50.0
    assert len(world.events) == 0

    # Tick past pulse active time
    mode.tick(world, balls, delta=0.1)
    assert abs(mode.pulse_timer - 3.05) < 0.001
    assert ball1.perception_radius == 1000.0
    assert len(world.events) == 1
    assert world.events[0][0] == "sound_pulse"

    # Tick past pulse reset time
    mode.pulse_timer = 3.45
    mode.tick(world, balls, delta=0.1)
    assert mode.pulse_timer == 0.0
    assert ball1.perception_radius == 50.0

