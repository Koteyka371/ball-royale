import pytest
from ai.game_modes import MovingHazardLinesMode
import random

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "brawler"
        self.team = "team1"
        self.hp = 100.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.events = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test_moving_hazard_line_mode():
    world = MockWorld()
    balls = [MockBall(1, 500, 500)]

    mode = MovingHazardLinesMode()
    mode.setup(world, balls)
    mode.spawn_interval = 1.0 # Make it spawn faster for test

    # Tick to spawn a line
    random.seed(42) # Make it predictable
    mode.tick(world, balls, 1.1)

    assert len(world.arena.hazards) > 0
    h = world.arena.hazards[0]
    assert h.kind == "deployable_thin_hazard_line"
    assert h.team == "environment"

    # Check that it moves
    start_x = getattr(h, "x", 0)
    start_y = getattr(h, "y", 0)

    mode.tick(world, balls, 1.0)

    end_x = getattr(h, "x", 0)
    end_y = getattr(h, "y", 0)

    assert start_x != end_x or start_y != end_y
