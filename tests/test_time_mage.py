import sys
import unittest

sys.path.insert(0, "src")

from ai.action import Action
from ai.ball_types_time_mage import TimeMage

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'clamp_position': lambda x,y: (x,y,False), 'hazards': [], 'update_zone': lambda dt: None})()
        self.balls = []
        self.events = []

    def add_event(self, name, payload):
        self.events.append((name, payload))

class TestTimeMage(unittest.TestCase):
    def test_time_rewind_self(self):
        world = MockWorld()
        mage = TimeMage(1, 100, 100)
        mage.team = "A"
        mage.hp = 10
        mage.state_history = [{"x": 0, "y": 0, "hp": 90}]
        world.balls.append(mage)

        action = Action(mage, world)
        action.ball.skill_timer = 0

        # Test time_rewind_self
        action._use_skill()

        self.assertEqual(mage.x, 0)
        self.assertEqual(mage.y, 0)
        self.assertEqual(mage.hp, 90)
        self.assertEqual(mage.state_history, [])

if __name__ == '__main__':
    unittest.main()
