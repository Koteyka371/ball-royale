import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ai.game_modes import EarthquakeEventMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append([name, data])

class MockBall:
    def __init__(self, grounded=False):
        self.ball_type = "player"
        self.id = "b1"
        self.hp = 100.0
        self.vx = 100.0
        self.vy = 100.0
        self.alive = True
        self.grounded = grounded

def test_earthquake_event_mode():
    mode = EarthquakeEventMode()
    world = MockWorld()
    ball_not_grounded = MockBall(grounded=False)
    ball_grounded = MockBall(grounded=True)
    balls = [ball_not_grounded, ball_grounded]

    # Tick down the initial timer (20.0 seconds)
    for _ in range(int(20.0 / 0.016)):
        mode.apply_dynamic_traits(world, balls, 0.016)

    assert not mode.is_shaking

    # Trigger earthquake
    mode.apply_dynamic_traits(world, balls, 0.016)

    assert mode.is_shaking

    # Apply effects during shaking
    mode.apply_dynamic_traits(world, balls, 0.016)

    # Camera shake event emitted
    shake_events = [e for e in world.events if e[0] == "camera_shake"]
    assert len(shake_events) > 0

    # Un-grounded ball takes damage and loses velocity
    assert ball_not_grounded.hp < 100.0
    assert ball_not_grounded.vx < 100.0
    assert ball_not_grounded.vy < 100.0

    # Grounded ball unaffected
    assert ball_grounded.hp == 100.0
    assert ball_grounded.vx == 100.0
    assert ball_grounded.vy == 100.0

def test_earthquake_event_death():
    mode = EarthquakeEventMode()
    world = MockWorld()
    ball = MockBall(grounded=False)
    ball.hp = 0.1
    balls = [ball]

    # Force start earthquake
    mode.is_shaking = True
    mode.shake_timer = 5.0

    mode.apply_dynamic_traits(world, balls, 0.016)

    assert not ball.alive
    death_events = [e for e in world.events if e[0] == "ball_died"]
    assert len(death_events) > 0
    assert death_events[0][1]["reason"] == "earthquake"
