import unittest
from ai.game_modes import MinefieldEventMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.alive = True
        self.hp = 100

    def take_damage(self, dmg):
        self.hp -= dmg

class TestMinefieldEventMode(unittest.TestCase):
    def test_minefield_event(self):
        mode = MinefieldEventMode()
        world = MockWorld()
        balls = [MockBall(100, 100)]

        # Loop until event triggers
        import random
        random.seed(42) # Set seed for predictability
        for _ in range(100):
            mode.event_timer = 21.0
            mode.tick(world, balls, delta=0.0)
            if mode.event_active:
                break

        self.assertTrue(mode.event_active)
        self.assertTrue(len(mode.mines) > 0)

        mine = mode.mines[0]
        balls[0].x = mine["x"]
        balls[0].y = mine["y"]

        mode.tick(world, balls, delta=1.0)
        self.assertEqual(balls[0].hp, 50)
        self.assertFalse(mine["active"])

if __name__ == '__main__':
    unittest.main()
