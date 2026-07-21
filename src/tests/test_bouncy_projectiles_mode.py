import unittest
from ai.game_modes import BouncyProjectilesMode
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, radius):
        bounced = False
        if x < radius: x = radius; bounced = True
        if x > 100 - radius: x = 100 - radius; bounced = True
        if y < radius: y = radius; bounced = True
        if y > 100 - radius: y = 100 - radius; bounced = True
        return x, y, bounced

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.width = 100
        self.height = 100
        self.game_mode = BouncyProjectilesMode()

    def get_nearby_entities(self, entity, radius):
        return [b for b in self.balls if b != entity]

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 100.0
        self.vy = 0.0
        self.radius = 5.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "projectile"
        self.team = 1
        self.bounces_left = 3

class MockHazard:
    def __init__(self):
        self.id = 99
        self.x = 50.0
        self.y = 50.0
        self.radius = 15.0
        self.kind = "hazard"
        self.hp = 100.0
        self.alive = True

class TestBouncyProjectilesMode(unittest.TestCase):
    def test_bounces_on_walls(self):
        world = MockWorld()
        ball = MockBall(1, 105.0, 50.0) # Past right wall (100)
        world.balls.append(ball)

        action = Action(ball.id, world)
        action.ball = ball

        bounced = action._clamp_position()
        self.assertTrue(bounced)
        self.assertEqual(ball.bounces_left, 2)
        self.assertEqual(ball.vx, -100.0)
        self.assertEqual(ball.vy, 0.0)
        self.assertTrue(ball.alive)

        # 2nd bounce
        ball.x = -5.0
        bounced = action._clamp_position()
        self.assertTrue(bounced)
        self.assertEqual(ball.bounces_left, 1)

        # 3rd bounce
        ball.x = 105.0
        bounced = action._clamp_position()
        self.assertTrue(bounced)
        self.assertEqual(ball.bounces_left, 0)

        # 4th bounce (should destroy)
        ball.x = -5.0
        bounced = action._clamp_position()
        self.assertTrue(bounced)
        self.assertFalse(ball.alive)
        self.assertEqual(ball.hp, 0.0)

    def test_bounces_on_hazards(self):
        world = MockWorld()
        ball = MockBall(1, 40.0, 50.0) # Approaching hazard at 50,50
        hazard = MockHazard()
        world.balls.extend([ball, hazard])

        action = Action(ball.id, world)
        action.ball = ball

        action._resolve_collisions()
        # Should bounce
        self.assertEqual(ball.bounces_left, 2)
        self.assertTrue(ball.vx < 0) # Reflected
        self.assertTrue(ball.alive)

        # Force bounces_left to 0 and bounce again
        ball.bounces_left = 0
        ball.x = 45.0 # reset pos to overlap
        ball.alive = True
        ball.hp = 100.0
        action._resolve_collisions()

        self.assertFalse(ball.alive)
        self.assertEqual(ball.hp, 0.0)

if __name__ == '__main__':
    unittest.main()
