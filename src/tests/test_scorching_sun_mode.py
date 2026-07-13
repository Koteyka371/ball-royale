import pytest
import os
import sys

# Ensure src/ is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import ScorchingSunMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.is_night = False
        self.weather = "clear"
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_name, event_data):
        self.events.append((event_name, event_data))

    def _deal_damage(self, target, source):
        pass

class MockBall:
    def __init__(self):
        self.x = 500
        self.y = 500
        self.alive = True
        self.hp = 100.0
        self.stamina = 100.0
        self.ball_type = "player"

def test_scorching_sun_mode_safe():
    mode = ScorchingSunMode()
    world = MockWorld()
    ball = MockBall()
    ball.x = 500
    ball.y = 500
    balls = [ball]

    mode.setup(world, balls)
    mode.tick(world, balls, 1.0)

    # Should not take damage because it is inside the safe zone
    assert ball.hp == 100.0
    assert ball.stamina == 100.0

def test_scorching_sun_mode_outside():
    mode = ScorchingSunMode()
    world = MockWorld()
    ball = MockBall()
    ball.x = 10
    ball.y = 10
    balls = [ball]

    mode.setup(world, balls)
    mode.tick(world, balls, 1.0)

    # Base damage is 10 per sec, heat multiplier initially 1, so roughly 10 damage
    assert ball.hp < 100.0
    # Stamina drain is 20 per sec
    assert ball.stamina < 100.0

def test_scorching_sun_mode_shrink():
    mode = ScorchingSunMode()
    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)

    initial_radius = mode.safe_zone_radius

    mode.tick(world, balls, 1.0)

    assert mode.safe_zone_radius < initial_radius

def test_scorching_sun_mode_heat_multiplier():
    mode = ScorchingSunMode()
    world = MockWorld()
    ball = MockBall()
    ball.x = 10
    ball.y = 10
    balls = [ball]

    mode.setup(world, balls)
    mode.tick(world, balls, 1.0)
    damage_first_sec = 100.0 - ball.hp

    # Advance timer significantly
    mode.timer = 60.0
    ball.hp = 100.0
    mode.tick(world, balls, 1.0)
    damage_later_sec = 100.0 - ball.hp

    assert damage_later_sec > damage_first_sec
