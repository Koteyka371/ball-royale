import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ai.game_modes import HazardBilliardsMode
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0.0
        self.vy = 0.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.radius = 10.0
        self.base_speed = 200.0
        self.damage = 10.0

def test_hazard_billiards():
    mode = HazardBilliardsMode()
    world = MockWorld()

    b1 = MockBall(1, 50, 50)
    b2 = MockBall(2, 200, 200)
    balls = [b1, b2]

    mode.setup(world, balls)

    assert b1.damage == 0.0
    assert b1.reflect_shield_active == True
    assert "hazard_billiards" in b1.mutators

    # Add a hazard
    h1 = MockHazard(60, 50, 10.0) # Near b1
    h2 = MockHazard(200, 180, 10.0) # Near b2
    world.arena.hazards = [h1, h2]

    # Tick to push hazard
    mode.tick(world, balls, 0.1)

    # b1 (50,50) should push h1 (60,50) to the right. dx=10, dy=0, dist=10 < 20. overlap=10.
    # nx=1, ny=0. h1.x = 60 + 10 = 70.
    # push_speed = base_speed = 200. vx += 1 * 200 * 0.1 * 5 = 100.

    assert h1.x > 60.0
    assert h1.vx > 0.0

    # Give h1 high velocity towards h2
    h1.x = 180
    h1.y = 180
    h1.vx = 200
    h1.vy = 200

    mode.tick(world, balls, 0.1)

    # h1 and h2 should collide
    print("Test passed")

if __name__ == "__main__":
    test_hazard_billiards()
