import pytest
from ai.game_modes import FrictionlessEventMode
import random

class MockBall:
    def __init__(self, ball_type="basic"):
        self.alive = True
        self.ball_type = ball_type
        self.is_frictionless = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

def test_frictionless_event_activation():
    orig_state = random.getstate()

    try:
        random.seed(1)

        mode = FrictionlessEventMode()
        world = MockWorld()
        b1 = MockBall()
        b2 = MockBall(ball_type="spectator")
        world.balls = [b1, b2]

        # The tick logic increments first, but if we pass delta=21.0,
        # it will be event_timer = 21.0, and since we just seeded, it WILL trigger.
        # Oh, if we pass delta=21.0, random.random() is evaluated inside the SAME tick.
        # Let's explicitly set timer and tick with 0.0 delta
        mode.event_timer = 21.0
        mode.tick(world, world.balls, 0.0)

        assert mode.event_active == True
        assert mode.event_duration >= 5.0 and mode.event_duration <= 15.0
        assert mode.event_timer == 0.0

        # Assert frictionless state on valid ball
        assert b1.is_frictionless == True
        # Assert spectator is untouched
        assert b2.is_frictionless == False

        # Assert event broadcast
        assert len(world.events) == 1
        assert world.events[0][0] == "frictionless_event"
        assert world.events[0][1]["active"] == True

        # Tick down duration
        mode.tick(world, world.balls, mode.event_duration)

        assert mode.event_active == False
        assert len(world.events) == 2
        assert world.events[1][0] == "frictionless_event"
        assert world.events[1][1]["active"] == False

        # Assert frictionless state is reverted
        assert b1.is_frictionless == False

    finally:
        random.setstate(orig_state)
