import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ai.game_modes import EarthquakeMode
import math

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self):
        self.alive = True
        self.ball_type = "player"
        self.vx = 0.0
        self.vy = 0.0
        self.time_since_death = 0.0

def test_earthquake_mode_event_and_impulse():
    mode = EarthquakeMode()
    world = MockWorld()
    ball1 = MockBall()
    ball2 = MockBall()
    balls = [ball1, ball2]

    # Force timer to trigger earthquake
    mode.earthquake_timer = 0.0
    mode.tick(world, balls, delta=0.1)

    # Check if screen_shake event was emitted
    assert len(world.events) > 0, "Earthquake mode should emit screen_shake events."
    assert world.events[0][0] == "screen_shake", "First event should be screen_shake"

    # Check if balls have vx/vy changed by impulse during earthquake
    assert ball1.vx != 0.0 or ball1.vy != 0.0, "Ball 1 should have vx/vy changed by impulse"
    assert ball2.vx != 0.0 or ball2.vy != 0.0, "Ball 2 should have vx/vy changed by impulse"
