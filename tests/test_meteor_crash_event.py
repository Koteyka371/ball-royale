import sys
import unittest
sys.path.insert(0, 'src')
from ai.game_modes import MeteorCrashEventMode
import math

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100

    def take_damage(self, amount):
        self.hp -= amount

class TestMeteorCrashEventMode(unittest.TestCase):
    def test_meteor_crash_lifecycle(self):
        mode = MeteorCrashEventMode()
        world = MockWorld()
        balls = [MockBall(200, 200)]

        import random
        random.seed(42)

        for _ in range(100):
            mode.event_timer = 21.0
            mode.tick(world, balls, delta=0.1)
            if mode.event_active:
                break

        self.assertTrue(mode.event_active)
        self.assertTrue(len(mode.meteors) >= 3)
        self.assertEqual(len(mode.craters), 0)

        first_meteor = mode.meteors[0]
        balls[0].x = first_meteor["x"]
        balls[0].y = first_meteor["y"]

        # Advance time incrementally until just after meteor crashes
        delay = first_meteor["delay"]
        time_passed = 0.0
        while time_passed <= delay:
            mode.tick(world, balls, delta=0.1)
            time_passed += 0.1

        self.assertTrue(len(mode.craters) > 0)
        # Should have taken 30 crash damage, plus maybe 0.1s of crater damage (1) => 69
        self.assertAlmostEqual(balls[0].hp, 69.0, places=0)

        # Reset HP for cleaner crater check
        balls[0].hp = 100

        crater = next(c for c in mode.craters if c["x"] == first_meteor["x"])
        initial_crater_hp = crater["hp"]

        mode.tick(world, balls, delta=1.0)

        self.assertAlmostEqual(balls[0].hp, 90.0, places=0) # Takes 10 damage/s
        self.assertAlmostEqual(crater["hp"], initial_crater_hp - 30.0, places=0) # Depleted by 30

        for _ in range(50): # 5 seconds of 30 dps = 150 dmg, enough to destroy
            mode.tick(world, balls, delta=0.1)
            if len([c for c in mode.craters if c["x"] == first_meteor["x"]]) == 0:
                break

        craters_at_spot = [c for c in mode.craters if c["x"] == first_meteor["x"]]
        self.assertEqual(len(craters_at_spot), 0)

        self.assertTrue(any(b.kind == "rare_material" for b in world.boosters))

if __name__ == '__main__':
    unittest.main()
