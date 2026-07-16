import unittest
import math
from ai.action import Action
from ai.ball_types_spy import Spy

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        return (x, y, False)

class MockBall:
    def __init__(self, id, team, color, ball_type, x, y, radius=10.0):
        self.id = id
        self.team = team
        self.color = color
        self.ball_type = ball_type
        self.BALL_TYPE = ball_type
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100.0
        self.alive = True
        self.damage = 20.0
        self.is_disguised = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = MockArena()
        self.next_id = 9999
        self.boosters = []
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [], 'allies': [], 'hazards': [], 'boosters': []}
    def _get_enemies(self):
        return []

class TestSpyDisguise(unittest.TestCase):
    def test_disguise_skill_and_explosion(self):
        world = MockWorld()
        spy = Spy(1, 100.0, 100.0)
        spy.team = "spy"
        spy.color = "black"
        spy.ball_type = "spy"
        spy.BALL_TYPE = "spy"
        spy.radius = 10.0
        world.balls.append(spy)

        enemy = MockBall(2, "red", "red", "warrior", 150.0, 150.0)
        world.balls.append(enemy)

        action = Action(spy, world)

        # Test applying disguise
        action.execute("use_skill", 0.1)

        self.assertTrue(spy.is_disguised)
        self.assertEqual(spy.team, "red")
        self.assertEqual(spy.color, "red")
        self.assertEqual(spy.ball_type, "warrior")
        self.assertEqual(spy.original_team, "spy")

        # Move closer to enemy to trigger explosion
        spy.x = 140.0
        spy.y = 140.0

        enemy.hp = 100.0
        # Tick to process explosion
        action.execute("idle", 0.1)

        self.assertFalse(spy.is_disguised)
        self.assertEqual(spy.team, "spy")
        self.assertEqual(spy.color, "black")

        # Enemy should have taken damage
        self.assertTrue(enemy.hp < 100.0)

if __name__ == '__main__':
    unittest.main()
