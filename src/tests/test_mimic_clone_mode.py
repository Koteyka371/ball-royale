import unittest
from ai.game_modes import GAME_MODES, MimicCloneMode

class MockBall:
    def __init__(self, id, x, y):
        self.id = id; self.x = x; self.y = y; self.hp = 100.0; self.max_hp = 100.0; self.alive = True
        self.vx = 0.0; self.vy = 0.0; self.active_skill = None; self.strategy = "attack"
        self.base_damage_multiplier = 1.0
        self.is_mimic_clone_mode = False
        self.mimic_swapped = False

class MockWorld:
    def __init__(self):
        self.balls = []; self.next_id = 9999

class TestMimicCloneMode(unittest.TestCase):
    def test_mode(self):
        mode = MimicCloneMode()
        world = MockWorld()
        b1 = MockBall(1, 100, 100)
        world.balls.append(b1)

        mode.tick(world, world.balls, 0.1)
        self.assertEqual(len(world.balls), 2)
        clone = world.balls[1]
        self.assertTrue(clone.is_mimic_clone_mode)
        self.assertEqual(clone.base_damage_multiplier, 0.5)

        b1.vx = 50.0
        b1.vy = 50.0
        b1.active_skill = "fireball"
        mode.tick(world, world.balls, 0.1)
        self.assertEqual(clone.vx, 50.0)
        self.assertEqual(clone.vy, 50.0)
        self.assertEqual(clone.active_skill, "fireball")

        clone.hp = 90  # took 10 dmg
        mode.tick(world, world.balls, 0.1)
        self.assertEqual(clone.hp, 80) # took another 10 dmg

        b1.hp = 0
        b1.alive = False
        mode.tick(world, world.balls, 0.1)
        self.assertTrue(b1.alive)
        self.assertEqual(b1.hp, 50.0)
        self.assertEqual(b1.x, clone.x)
        self.assertEqual(b1.max_hp, 50.0)
        self.assertEqual(b1.base_damage_multiplier, 0.5)
        self.assertFalse(clone.alive)

if __name__ == '__main__':
    unittest.main()
