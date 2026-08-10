import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "player"

def test_black_hole_boundaries():
    mode = GAME_MODES["black_hole_boundaries"]
    world = MockWorld()
    b = MockBall(100.0, 100.0)
    balls = [b]

    mode.setup(world, balls)

    # Before activation, shouldn't move
    mode.apply_dynamic_traits(world, balls, 15.0)
    assert b.vx == 0.0
    assert b.vy == 0.0

    # After activation, should get pulled
    mode.apply_dynamic_traits(world, balls, 16.0) # total 31.0 seconds > 30.0

    assert b.vx > 0.0
    assert b.vy > 0.0

    assert len(world.events) == 1
    assert world.events[0][0] == "black_hole_boundaries_activated"
