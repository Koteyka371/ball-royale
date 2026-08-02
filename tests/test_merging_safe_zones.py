import pytest
from src.ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.events = []

    def add_event(self, event_type, data):
        self.events.append(data)

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"
        self.hp = 100

def test_merging_safe_zones():
    mode = GAME_MODES["merging_safe_zones"]
    world = MockWorld()

    # We create some balls
    balls = [MockBall(500, 500), MockBall(10, 10)]

    mode.setup(world, balls)

    # Ensure 3-4 zones were created
    assert 3 <= len(mode.zones) <= 4

    # Run a tick
    mode.tick(world, balls, delta=1.0)

    # Check that merge_progress increased
    assert mode.merge_progress > 0

    # Ball 1 should be outside the safe zones (at 10, 10) while center zones are around 500,500
    assert balls[1].hp < 100
