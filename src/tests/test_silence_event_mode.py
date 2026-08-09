import pytest
import sys
import math

sys.path.append("src")

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x=0, y=0, alive=True):
        self.x = x
        self.y = y
        self.alive = alive
        self.silence_timer = 0.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, t, d):
        self.events.append(d)

def test_silence_event_mode():
    world = MockWorld()
    b1 = MockBall(alive=True)
    b2 = MockBall(alive=True)
    balls = [b1, b2]

    mode = GAME_MODES["silence_event"]
    mode.event_timer = 20.1
    mode.event_active = False

    # Simulate ticking until it triggers
    import random
    original_random = random.random
    try:
        random.random = lambda: 0.05  # Force trigger
        mode.tick(world, balls, delta=0.016)
    finally:
        random.random = original_random

    assert mode.event_active == True
    assert mode.event_duration > 9.9  # It should subtract 0.016

    # Check if event was emitted
    assert len(world.events) > 0
    assert world.events[0]["type"] == "silence_event"

    # Check if silence timer is applied to balls
    assert b1.silence_timer >= 0.5
    assert b2.silence_timer >= 0.5
