import sys
import unittest

sys.path.insert(0, "src")

from ai.action import Action

class MockBall:
    def __init__(self, x, y, hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100
        self.team = "A"
        self.state_history = [{"x": x - 10, "y": y - 10, "hp": hp + 20}]
        self.stun_timer = 5.0
        self.silence_timer = 0.0
        self.is_stunned = True
        self.poison_timer = 5.0
        self.skill_timer = 0
        self.id = 1
        self.skills = ["tactical_rewind"]
        self.active_skill = "tactical_rewind"
        self.skill = "tactical_rewind"
        self.alive = True
        self.vx = 0
        self.vy = 0

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'clamp_position': lambda *args, **kwargs: (0,0,False), 'hazards': [], 'update_zone': lambda *args, **kwargs: None})()
        self.balls = []
        self.events = []
        self.solar_flare_active = False

    def add_event(self, name, payload):
        self.events.append((name, payload))

class TestTacticalRewind(unittest.TestCase):
    def test_tactical_rewind(self):
        world = MockWorld()
        ball = MockBall(50, 50, 50)
        world.balls.append(ball)

        action = Action(ball, world)

        # Test tactical_rewind
        action.ball.skill_timer = 0
        action._use_skill()

        self.assertEqual(ball.x, 40)
        self.assertEqual(ball.y, 40)
        self.assertEqual(ball.hp, 70)
        self.assertEqual(ball.state_history, [])
        self.assertEqual(ball.stun_timer, 0.0)
        self.assertEqual(ball.silence_timer, 0.0)
        self.assertFalse(ball.is_stunned)
        self.assertEqual(ball.poison_timer, 0.0)

if __name__ == '__main__':
    unittest.main()
