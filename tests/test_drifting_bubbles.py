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

def test_drifting_bubbles():
    mode = CollapsingBubblesMode()
    world = MockWorld()
    ball1 = MockBall(500, 500)

    mode.setup(world, [ball1])

    assert len(mode.bubbles) == 5, "Should spawn 5 initial bubbles"

    # Set known velocity for first bubble
    mode.bubbles[0]["x"] = 500
    mode.bubbles[0]["y"] = 500
    mode.bubbles[0]["vx"] = 10
    mode.bubbles[0]["vy"] = -10

    # Fast forward time to trigger drift
    mode.tick(world, [ball1], delta=1.0)

    assert mode.bubbles[0]["x"] == 510, "Bubble should drift right"
    assert mode.bubbles[0]["y"] == 490, "Bubble should drift up"

    # Test bouncing off walls
    mode.bubbles[0]["x"] = mode.bubbles[0]["radius"] - 1 # past left wall
    mode.bubbles[0]["vx"] = -10

    mode.tick(world, [ball1], delta=1.0)
    assert mode.bubbles[0]["vx"] == 10, "Bubble should bounce off left wall"
    assert mode.bubbles[0]["x"] == mode.bubbles[0]["radius"], "Bubble should reset x"
