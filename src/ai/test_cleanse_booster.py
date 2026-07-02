import unittest
from ai.action import Action

class MockEntity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockBall(MockEntity):
    def __init__(self):
        super().__init__(
            id=1, x=0.0, y=0.0, radius=10.0, speed=2.0, hp=100.0, max_hp=50.0,
            alive=True, ball_type="default", team="A", inventory=[],
            burn_timer=5.0, poison_timer=10.0, silence_timer=2.0,
            zone_immunity_timer=0.0
        )

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []

class TestCleanseBooster(unittest.TestCase):
    def test_cleanse_booster(self):
        ball = MockBall()
        world = MockWorld()
        world.balls = [ball]

        cleanse = MockEntity(id=2, x=0.0, y=0.0, kind="cleanse_booster", active=True)
        world.boosters = [cleanse]

        action = Action(ball, world)
        action.execute("collect_booster", 1.0)

        self.assertEqual(ball.burn_timer, 0.0)
        self.assertEqual(ball.poison_timer, 0.0)
        self.assertEqual(ball.silence_timer, 0.0)

        self.assertEqual(ball.max_hp, 100.0)

        self.assertEqual(ball.zone_immunity_timer, 5.0)
        self.assertNotIn(cleanse, world.boosters)

if __name__ == '__main__':
    unittest.main()
