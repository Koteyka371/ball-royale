import unittest
from ai.game_modes import RadiationWindMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self):
        self.alive = True
        self.ball_type = "normal"
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0.0
            self.alive = False

class TestRadiationWindMode(unittest.TestCase):
    def test_radiation_wind_mode(self):
        mode = RadiationWindMode()
        world = MockWorld()
        ball_in = MockBall()
        ball_out = MockBall()
        ball_out.x = -10.0  # Out of bounds

        balls = [ball_in, ball_out]
        mode.setup(world, balls)

        # Test tick (wind + damage)
        mode.tick(world, balls, delta=1.0)

        # Wind check
        self.assertNotEqual(ball_in.vx, 0.0)
        self.assertNotEqual(ball_in.vy, 0.0)

        # Damage check
        self.assertEqual(ball_in.hp, 100.0) # In bounds, no damage
        self.assertEqual(ball_out.hp, 0.0)  # Takes 500 damage and dies
        self.assertFalse(ball_out.alive)

if __name__ == '__main__':
    unittest.main()
