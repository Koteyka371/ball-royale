import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True

def test_massive_black_hole_pull_and_damage():
    assert "massive_black_hole" in GAME_MODES
    mode = GAME_MODES["massive_black_hole"]

    world = MockWorld()

    # Ball 1 is far from center
    # Center is 1000, 1000
    ball_far = MockBall(1, 100, 100)

    # Ball 2 is close to center
    ball_close = MockBall(2, 900, 900)

    balls = [ball_far, ball_close]

    mode.setup(world, balls)

    initial_x_far = ball_far.x
    initial_x_close = ball_close.x

    # Run a tick
    delta = 1.0
    mode.tick(world, balls, delta)

    # Verify balls get pulled towards center (1000, 1000)
    assert ball_far.x > initial_x_far
    assert ball_far.y > 100
    assert ball_close.x > initial_x_close
    assert ball_close.y > 900

    # Verify ball_close took more damage than ball_far
    damage_far = 100.0 - ball_far.hp
    damage_close = 100.0 - ball_close.hp

    assert damage_close > damage_far
    assert damage_close > 0
