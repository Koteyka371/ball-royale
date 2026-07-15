import unittest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 20.0
        self.alive = True
        self.hp = 100.0

class MockWorld:
    pass

class TestMagneticMineZoneMode(unittest.TestCase):
    def setUp(self):
        self.mode = GAME_MODES.get("magnetic_mine_zone")
        self.world = MockWorld()

    def test_mine_tracking(self):
        balls = [MockBall(200.0, 200.0, 150.0, 0.0)] # fast ball
        self.mode.setup(self.world, balls)

        self.mode.mines = [{
            "x": 300.0,
            "y": 200.0,
            "radius": 15.0,
            "damage": 50.0,
            "active": True
        }]

        m = self.mode.mines[0]
        self.assertEqual(m["x"], 300.0)

        self.mode.tick(self.world, balls, delta=1.0)

        self.assertTrue(m["x"] < 300.0)

    def test_mine_no_tracking(self):
        balls = [MockBall(200.0, 200.0, 10.0, 0.0)] # slow ball
        self.mode.setup(self.world, balls)

        self.mode.mines = [{
            "x": 300.0,
            "y": 200.0,
            "radius": 15.0,
            "damage": 50.0,
            "active": True
        }]

        m = self.mode.mines[0]
        self.assertEqual(m["x"], 300.0)

        self.mode.tick(self.world, balls, delta=1.0)

        self.assertEqual(m["x"], 300.0)

if __name__ == '__main__':
    unittest.main()
