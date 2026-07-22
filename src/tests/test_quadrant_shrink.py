import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.radius = 10
    def take_damage(self, amount):
        self.hp -= amount

def test_quadrant_shrink_mode():
    mode = GAME_MODES.get('quadrant_shrink')
    assert mode is not None

    world = MockWorld()
    b1 = MockBall(250, 250) # Safe in Q0
    b2 = MockBall(50, 50)   # Outside safe zone in Q0
    balls = [b1, b2]

    mode.setup(world, balls)

    for _ in range(10):
        mode.tick(world, balls, delta=0.1)

    assert b1.hp == 100
    assert b2.hp < 100

    b3 = MockBall(250, 500) # On the portal from Q0 to Q1
    b3.radius = 10
    mode.tick(world, [b3], delta=0.1)

    assert b3.x == 750
    assert b3.y == 250
