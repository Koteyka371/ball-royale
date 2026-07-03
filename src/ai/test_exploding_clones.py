import unittest
from ai.game_modes import ExplodingClonesMode

class MockBall:
    def __init__(self, x, y, hp=100, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100
        self.alive = alive
        self.is_exploding_clone = False
        self.has_exploded = False
        self.skill_timer = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class TestExplodingClonesMode(unittest.TestCase):
    def test_exploding_clone_explosion(self):
        mode = ExplodingClonesMode()
        world = MockWorld()

        clone = MockBall(50, 50, hp=0, alive=False)
        clone.is_exploding_clone = True

        target = MockBall(55, 55, hp=100, alive=True)
        far_target = MockBall(200, 200, hp=100, alive=True)

        world.balls = [clone, target, far_target]

        mode.tick(world, world.balls, 0.016)

        self.assertTrue(clone.has_exploded)
        self.assertTrue(target.hp < 100)
        self.assertEqual(far_target.hp, 100)
        self.assertTrue(any(e[0] == "explosion" for e in world.events))

if __name__ == '__main__':
    unittest.main()
