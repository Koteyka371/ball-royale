import unittest
from ai.action import Action

class MockBall:
    def __init__(self, x, y, hp=100):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.hp = hp
        self.max_hp = 100
        self.alive = True
        self.inventory = ["position_swap"]
        self.skill = ""

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 500

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.entities = balls
        self.arena = MockArena()

class TestPositionSwap(unittest.TestCase):
    def test_position_swap_deals_damage_and_slows(self):
        ball1 = MockBall(0, 0)
        ball2 = MockBall(100, 100)
        world = MockWorld([ball1, ball2])

        action = Action(ball1, world)

        # We need to simulate action.execute(delta=1.0)
        # To trigger 'flee', we can set health low compared to max_hp, and have an enemy nearby.
        ball1.hp = 10

        action.execute("flee", 1.0)

        # Since physics applies, positions might not be exactly 100/100, but we can check if they moved a lot.
        self.assertGreater(ball1.x, 50)
        self.assertGreater(ball1.y, 50)

        self.assertLess(ball2.x, 50)
        self.assertLess(ball2.y, 50)

        # Check damage
        self.assertEqual(ball2.hp, 95)

        # Check slow
        self.assertEqual(getattr(ball2, "speed_debuff_timer", 0), 2.0)

        # Check item consumed
        self.assertNotIn("position_swap", ball1.inventory)

if __name__ == "__main__":
    unittest.main()
