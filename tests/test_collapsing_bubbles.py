import sys
import math
sys.path.insert(0, "src")
from unittest.mock import MagicMock
from ai.game_modes import CollapsingBubblesMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

    def add_event(self, event_type, data):
        pass

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.id = 1
        self.weather_immunity_timer = 0.0

def test_collapsing_bubbles():
    mode = CollapsingBubblesMode()
    world = MockWorld()
    ball1 = MockBall(500, 500)

    mode.setup(world, [ball1])

    assert len(mode.bubbles) == 5, "Should spawn 5 initial bubbles"

    # Position ball exactly at center of first bubble
    ball1.x = mode.bubbles[0]["x"]
    ball1.y = mode.bubbles[0]["y"]

    mode.tick(world, [ball1], delta=1.0)

    assert ball1.hp == 100.0, "Ball safely inside bubble should not take damage"

    # Fast forward time to trigger collapse
    mode.bubbles[0]["timer"] = -0.1
    mode.tick(world, [ball1], delta=0.016)

    assert mode.bubbles[0]["collapsing"] is True, "Bubble should start collapsing"
    assert mode.bubbles[0]["radius"] < 250.0, "Bubble radius should decrease"

def test_outside_damage():
    mode = CollapsingBubblesMode()
    world = MockWorld()
    ball2 = MockBall(-1000, -1000) # definitely outside all bubbles

    mode.setup(world, [ball2])
    mode.tick(world, [ball2], delta=1.0)

    assert ball2.hp < 100.0, "Ball outside bubbles should take damage"
