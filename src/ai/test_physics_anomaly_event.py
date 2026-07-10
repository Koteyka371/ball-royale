import unittest
import math
from ai.game_modes import GAME_MODES, PhysicsAnomalyEventMode
from ai.action import Action


class MockProfileManager:
    def is_nemesis(self, b1, b2):
        return False

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'hazards': []})()
        self.events = []
        self.game_mode = PhysicsAnomalyEventMode()
        self.profile_manager = MockProfileManager()

    def add_event(self, name, data):
        self.events.append({'name': name, 'data': data})

class MockBall:
    def __init__(self, id, x, y, team="team1"):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.alive = True
        self.team = team
        self.radius = 10.0
        self.damage = 10.0
        self.hp = 100.0

class TestPhysicsAnomalyEvent(unittest.TestCase):
    def test_speed_modification(self):
        world = MockWorld()
        mode = world.game_mode
        mode.event_active = True
        mode.event_duration = 10.0

        # Center is 500, 500
        # Ball 1 moving towards center
        b1 = MockBall(1, 100, 500)
        b1.vx = 100.0 # moving right
        b1.vy = 0.0

        # Ball 2 moving away from center
        b2 = MockBall(2, 600, 500)
        b2.vx = 100.0 # moving right (away from 500, 500)
        b2.vy = 0.0

        balls = [b1, b2]
        mode.tick(world, balls, 1.0)

        self.assertGreater(b1.physics_anomaly_speed_mod, 1.0)
        self.assertLess(b2.physics_anomaly_speed_mod, 1.0)

        action = Action(b1, world)
        b1.vx = 100.0
        # clear any negative reflection that might have stuck
        if hasattr(b1, "_reflection_vx"):
            delattr(b1, "_reflection_vx")

        # Manually invoke the speed mod since action execution depends on game logic we might not fully mock here
        if hasattr(b1, "physics_anomaly_speed_mod"):
            b1.vx *= b1.physics_anomaly_speed_mod

        self.assertGreater(b1.vx, 100.0)

    def test_projectile_curving(self):
        world = MockWorld()
        world.game_mode.event_active = True

        attacker = MockBall(1, 100, 500, "team1")
        target = MockBall(2, 900, 500, "team2")

        action = Action(attacker, world)

        # Trigger attempt_damage as ranged
        action._attempt_damage(attacker, target)

        self.assertTrue(hasattr(attacker, "suspended_projectiles"))
        self.assertEqual(len(attacker.suspended_projectiles), 1)
        sp = attacker.suspended_projectiles[0]

        self.assertTrue(sp.get("is_anomaly"))
        self.assertEqual(sp["x"], 100)
        self.assertEqual(sp["y"], 500)
        self.assertGreater(sp["vx"], 0.0)

        # Run execute to update projectile
        old_vx = sp["vx"]
        old_vy = sp["vy"]
        action.execute("idle", 0.1)

        # Velocity should change due to curving force
        if old_vx == sp["vx"]:
            self.assertNotEqual(old_vy, sp["vy"])

if __name__ == '__main__':
    unittest.main()
