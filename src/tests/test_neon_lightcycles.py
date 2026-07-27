import unittest
from ai.neon_lightcycles import NeonLightcyclesMode

class MockBall:
    def __init__(self, x=0, y=0, speed=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = 100
        self.alive = alive
        self.speed = speed
        self.base_speed = speed

class MockWorld:
    def _deal_damage(self, source, target, amount):
        target.hp -= amount
        if target.hp <= 0:
            target.hp = 0
            target.alive = False

class TestNeonLightcyclesMode(unittest.TestCase):
    def test_setup(self):
        mode = NeonLightcyclesMode()
        world = MockWorld()
        ball = MockBall(speed=100.0)
        mode.setup(world, [ball])

        self.assertEqual(ball.lightcycle_trail, [])
        self.assertEqual(ball.last_pos, (0, 0))
        self.assertGreaterEqual(ball.speed, 400.0)
        self.assertGreaterEqual(ball.base_speed, 400.0)

    def test_tick_creates_trail(self):
        mode = NeonLightcyclesMode()
        world = MockWorld()
        ball = MockBall(speed=400.0)
        mode.setup(world, [ball])

        # Move ball significantly
        ball.x = 20
        ball.y = 0
        mode.tick(world, [ball], 0.1)

        self.assertEqual(len(ball.lightcycle_trail), 1)
        self.assertEqual(ball.lightcycle_trail[0], ((0, 0), (20, 0)))
        self.assertEqual(ball.last_pos, (20, 0))

    def test_intersection_kills(self):
        mode = NeonLightcyclesMode()
        world = MockWorld()

        ball1 = MockBall(x=0, y=10)
        ball2 = MockBall(x=10, y=0)
        mode.setup(world, [ball1, ball2])

        # Ball 1 creates a trail from (0,10) to (20,10)
        ball1.x = 20
        mode.tick(world, [ball1, ball2], 0.1)

        # Ball 2 moves from (10,0) to (10,20), crossing ball 1's trail
        ball2.x = 10
        ball2.y = 20
        mode.tick(world, [ball1, ball2], 0.1)

        self.assertTrue(ball1.alive)
        self.assertFalse(ball2.alive)
        self.assertEqual(ball2.hp, 0)

if __name__ == '__main__':
    unittest.main()
