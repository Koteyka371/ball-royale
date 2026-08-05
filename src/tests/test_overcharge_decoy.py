import unittest
import math
from ai.action import Action

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls or []
        self.events = []

    def get_nearby_entities(self, b, radius):
        return []

class MockBall:
    def __init__(self, **kwargs):
        self.alive = True
        self.team = "A"
        self.ball_type = "A"
        self.hp = 100
        self.is_confused = False
        self.confusion_timer = 0.0
        self.id = 1
        self.decoy_timer = 10.0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def take_damage(self, amt):
        self.hp -= amt
        if self.hp <= 0:
            self.alive = False

class TestDecoyCloneOvercharge(unittest.TestCase):
    def test_normal_explosion_radius(self):
        # Enemy at dist 220, normal explosion is 120, aura is 200
        enemy1 = MockBall(id=2, team="B", ball_type="B", x=220, y=0, hp=100)
        decoy = MockBall(id=1, is_decoy_clone=True, mimic_timer=0, _exploded=False, x=0, y=0, hp=100, is_overcharged=False)
        w = MockWorld([decoy, enemy1])

        a = Action(decoy, w)
        a.execute("defend", 0.016)

        self.assertFalse(decoy.alive)
        self.assertTrue(decoy._exploded)

        self.assertEqual(enemy1.hp, 100)
        self.assertFalse(enemy1.is_confused)

    def test_overcharge_explosion_radius(self):
        # Enemy at dist 220, normal is 120, overcharged is 240, aura is 200
        enemy1 = MockBall(id=2, team="B", ball_type="B", x=220, y=0, hp=100)
        decoy = MockBall(id=1, is_decoy_clone=True, mimic_timer=0, _exploded=False, x=0, y=0, hp=100, is_overcharged=True)
        w = MockWorld([decoy, enemy1])

        a = Action(decoy, w)
        a.execute("defend", 0.016)

        self.assertFalse(decoy.alive)
        self.assertTrue(decoy._exploded)

        self.assertEqual(enemy1.hp, 50)
        self.assertTrue(enemy1.is_confused)
        self.assertGreater(enemy1.confusion_timer, 2.0)

if __name__ == "__main__":
    unittest.main()
