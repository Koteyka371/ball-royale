import sys
import unittest

sys.path.insert(0, "src")

from ai.action import Action
from ai.ball_types_echo_weaver import EchoWeaver

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'clamp_position': lambda *args: (args[1],args[2],False), 'hazards': [], 'update_zone': lambda dt, d1=0, d2=0: None})()
        self.balls = []
        self.events = []
        self.time = 0.0

    def add_event(self, name, payload):
        self.events.append((name, payload))

    def get_nearby_entities(self, ball, radius):
        return []

class TestEchoRewind(unittest.TestCase):
    def test_echo_rewind(self):
        world = MockWorld()
        weaver = EchoWeaver(1, 100, 100)
        weaver.team = "A"
        weaver.hp = 100
        world.balls.append(weaver)

        action = Action(weaver, world)

        # Test first activation - start recording
        weaver.skill_timer = 0
        action._use_skill()

        self.assertTrue(weaver.is_echo_recording)
        self.assertEqual(weaver.echo_rewind_timer, 5.0)
        self.assertEqual(weaver.echo_rewind_state["x"], 100)
        self.assertEqual(weaver.echo_rewind_state["y"], 100)
        self.assertEqual(weaver.echo_rewind_state["hp"], 100)

        # Move and take damage
        weaver.x = 200
        weaver.y = 200
        weaver.hp = 50
        weaver.is_stunned = True
        weaver.stun_timer = 2.0

        # Test second activation - rewind
        weaver.skill_timer = 0
        action._use_skill()

        self.assertFalse(weaver.is_echo_recording)
        self.assertEqual(weaver.x, 100)
        self.assertEqual(weaver.y, 100)
        self.assertEqual(weaver.hp, 100)
        self.assertFalse(weaver.is_stunned)
        self.assertEqual(weaver.stun_timer, 0.0)

    def test_echo_rewind_timeout(self):
        world = MockWorld()
        weaver = EchoWeaver(1, 100, 100)
        weaver.team = "A"
        world.balls.append(weaver)

        action = Action(weaver, world)

        # Start recording
        weaver.skill_timer = 0
        action._use_skill()
        self.assertTrue(weaver.is_echo_recording)

        # Wait for timeout (5.1 seconds)
        action.execute("idle", 5.1)

        self.assertFalse(weaver.is_echo_recording)
        self.assertEqual(weaver.echo_rewind_timer, 0.0)

if __name__ == '__main__':
    unittest.main()
