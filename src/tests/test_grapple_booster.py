import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.team = 1
        self.grapple_booster_timer = 5.0
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_grapple_booster():
    ball = MockBall(500.0, 500.0)
    world = MockWorld()
    action = Action(ball, world)
    action.execute("idle", 0.1)

if __name__ == "__main__":
    test_grapple_booster()
    print("Test passed.")
