import unittest
import math
from ai.game_modes import GAME_MODES


class MockBall:
    def __init__(self, x, y, id="1"):
        self.x = x
        self.y = y
        self.id = id
        self.alive = True
        self.stun_timer = 0.0
        self.radius = 15.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []
    def add_event(self, type, data):
        self.events.append((type, data))
    def _deal_damage(self, attacker, target, amt):
        pass

class TestLightningStrikeEventMode(unittest.TestCase):
    def setUp(self):
        self.mode = GAME_MODES["lightning_strike_event"]
        self.mode.event_timer = 0.0
        self.mode.event_active = False
        self.mode.strikes = []

        self.world = MockWorld()
        self.world.arena = MockArena()
        self.world.events = []
        self.world.dead_balls = []

    def test_lightning_strike_lifecycle(self):
        balls = [MockBall(200, 200)]

        # Advance timer
        self.mode.event_timer = 11.0
        import random
        random.seed(1)

        # Keep ticking until event triggers
        max_ticks = 100
        ticks = 0
        while not self.mode.event_active and ticks < max_ticks:
            self.mode.event_timer = 11.0
            self.mode.tick(self.world, balls, 0.016)
            ticks += 1

        self.assertTrue(self.mode.event_active)
        self.assertTrue(len(self.mode.strikes) > 0)

        # Check warning event
        has_warning_event = any(e[0] == "lightning_warning" for e in self.world.events)
        self.assertTrue(has_warning_event)

        # Force a strike on top of the ball
        s = self.mode.strikes[0]
        s["x"] = 200
        s["y"] = 200
        s["timer"] = 0.016 # Trigger next tick
        s["state"] = "warning"

        self.mode.tick(self.world, balls, 0.016)

        # Check stun applied
        self.assertEqual(s["state"], "active")
        self.assertTrue(balls[0].stun_timer >= 2.0)

        has_stun_event = any(e[0] == "stun" and e[1].get("id") == "1" for e in self.world.events)
        self.assertTrue(has_stun_event)

        has_strike_event = any(e[0] == "lightning_strike" for e in self.world.events)
        self.assertTrue(has_strike_event)

        # Check hazard synchronization
        hazard_kinds = [h.kind for h in self.world.arena.hazards]
        self.assertIn("lightning_strike", hazard_kinds)

if __name__ == '__main__':
    unittest.main()
