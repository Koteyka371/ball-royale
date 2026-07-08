import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import BodySwapMode

class MockBall:
    def __init__(self, id, x, y, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = alive

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_body_swap_mode():
    mode = BodySwapMode()
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 200, 200)
    balls = [b1, b2]

    mode.setup(world, balls)

    # 9 seconds pass, no swap
    mode.tick(world, balls, delta=9.0)
    assert b1.x == 100 and b1.y == 100
    assert b2.x == 200 and b2.y == 200

    # 1 second passes, reaches 10.0
    mode.tick(world, balls, delta=1.0)

    # b1 and b2 should have swapped places
    assert (b1.x == 200 and b2.x == 100) or (b1.x == 100 and b2.x == 200)
