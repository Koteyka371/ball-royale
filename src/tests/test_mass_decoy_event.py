import unittest
from unittest.mock import MagicMock
from ai.game_modes import MassDecoyEventMode, GAME_MODES

class MockBall:
    def __init__(self, bid, btype, is_decoy=False, alive=True):
        self.id = bid
        self.ball_type = btype
        self.is_decoy = is_decoy
        self.alive = alive
        self.x = 100
        self.y = 100
        self.speed = 100
        self.damage = 10

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.next_id = 900
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class TestMassDecoyEvent(unittest.TestCase):
    def test_spawn(self):
        mode = MassDecoyEventMode()
        w = MockWorld()
        b1 = MockBall(1, "normal", False, True)
        b2 = MockBall(2, "spectator", False, True)
        b3 = MockBall(3, "normal", True, True)
        w.balls = [b1, b2, b3]

        mode.tick(w, w.balls, 15.1)

        self.assertEqual(len(w.balls), 4) # 3 original + 1 decoy
        new_decoy = w.balls[-1]
        self.assertTrue(new_decoy.is_decoy)
        self.assertEqual(new_decoy.ball_type, "mimic_decoy")
        self.assertEqual(new_decoy.speed, 0.0)
        self.assertEqual(new_decoy.damage, 0.0)

if __name__ == '__main__':
    unittest.main()
