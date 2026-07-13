import sys
import unittest

sys.path.append('src')
from ai.game_modes import BattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.kill_log = []
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 80
        self.team = team
        self.max_hp = 100
        self.radius = 15.0
        self.ball_type = team
        self.traits = []

class TestCapturePoints(unittest.TestCase):
    def test_capture_points(self):
        mode = BattleRoyaleMode()
        w = MockWorld()
        b1 = MockBall(1, 100, 100, "teamA")
        b2 = MockBall(2, 500, 500, "teamB")

        mode.setup(w, [b1, b2])
        self.assertEqual(len(mode.capture_points), 3)

        # Move b1 into the first capture point
        cp = mode.capture_points[0]
        cp["x"] = 100
        cp["y"] = 100

        # It should start capturing
        mode.tick(w, [b1, b2], 1.0)
        self.assertEqual(cp["capture_progress"], 15.0)

        # fully capture it
        mode.tick(w, [b1, b2], 10.0)
        self.assertEqual(cp["captured_by"], "teamA")

        # Test advantages
        self.assertEqual(b1.hp, min(b1.max_hp, 80 + 5.0 * 10.0)) # heals up to max_hp
        self.assertTrue(getattr(b2, "revealed", False))

if __name__ == '__main__':
    unittest.main()
