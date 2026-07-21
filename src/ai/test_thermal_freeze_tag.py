import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, ball_type="warrior", team="Red"):
        self.id = id
        self.ball_type = ball_type
        self.team = team
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.is_frozen = False
        self.hp = 100.0
        self.max_hp = 100.0
        self._frost_last_hp = 100.0

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.id = 1
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = 0
        self.duration = 15.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class TestThermalFreezeTagMode(unittest.TestCase):
    def setUp(self):
        self.mode = GAME_MODES["thermal_freeze_tag"]
        self.world = MockWorld()

    def test_thawing_in_heat_zone(self):
        ball = MockBall(1)
        ball.x = 500
        ball.y = 500
        ball.is_frozen = True
        ball.frozen_timer = 9999
        ball.stun_timer = 9999

        hazard = MockHazard("heat_zone", 500, 500, 150)
        self.world.arena.hazards.append(hazard)

        self.mode.tick(self.world, [ball], 2.0)
        self.assertTrue(ball.is_frozen)

        self.mode.tick(self.world, [ball], 1.5)
        self.assertFalse(ball.is_frozen)
        self.assertEqual(ball.stun_timer, 0.0)

    def test_shattering_in_frost_zone(self):
        ball = MockBall(1)
        ball.x = 500
        ball.y = 500
        ball.is_frozen = True

        hazard = MockHazard("frost_zone", 500, 500, 150)
        self.world.arena.hazards.append(hazard)

        self.mode.tick(self.world, [ball], 1.0)
        self.assertTrue(ball.alive)
        self.assertEqual(ball.hp, 100)

        ball.hp = 90
        self.mode.tick(self.world, [ball], 0.1)
        self.assertFalse(ball.alive)
        self.assertEqual(ball.hp, 0)

if __name__ == '__main__':
    unittest.main()
