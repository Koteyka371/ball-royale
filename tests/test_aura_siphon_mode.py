import sys
import unittest
sys.path.append("src")
from ai.action import Action

class MockMode:
    def __init__(self, name):
        self.name = name

class MockWorld:
    def __init__(self, mode_name):
        self.balls = []
        self.game_mode = MockMode(mode_name)

class MockBall:
    def __init__(self, id, team, ball_type, x, y):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed = 100.0
        self.damage = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True

class TestAuraSiphonMode(unittest.TestCase):
    def test_aura_siphon_mode(self):
        world = MockWorld("Aura Siphon")
        b1 = MockBall(1, "team1", "typeA", 0, 0)
        b2 = MockBall(2, "team2", "typeB", 10, 0)
        b3 = MockBall(3, "team2", "typeC", 20, 0)
        b4 = MockBall(4, "team2", "typeD", 30, 0)

        # In Aura Siphon mode, enemies near b1 (b2, b3, b4) will buff b1's stats
        world.balls = [b1, b2, b3, b4]

        action = Action(b1, world)
        action._apply_friendly_aura(0.016)

        # 3 unique enemies = 3 stacks
        # 3 stacks -> damage multiplier 1 + 0.2*1 = 1.2 -> 12.0
        self.assertGreater(b1.speed, 100.0)
        self.assertGreater(b1.damage, 10.0)

if __name__ == "__main__":
    unittest.main()
