import unittest
from ai.action import Action

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.hp = 100.0
        self.alive = True
        self.damage = 10.0
        self.skill = "mimic_clone"
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        return (x, y, False)

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = MockArena()
        self.next_id = 9999
    def get_nearby_entities(self, ball, radius):
        return {'enemies': []}

class TestMimicCloneSwap(unittest.TestCase):
    def test_mimic_clone_swap(self):
        world = MockWorld()

        my_ball = MockBall(id=1, x=100.0, y=100.0)
        world.balls.append(my_ball)

        # Test 1: no clone exists, should create one
        action = Action(my_ball, world)
        my_ball.active_skill = "mimic_clone"
        action.execute("use_skill", 0.1)

        # Check if clone created
        clones = [b for b in world.balls if getattr(b, "is_mimic_clone", False)]
        self.assertEqual(len(clones), 1)
        clone = clones[0]
        self.assertEqual(clone.mimic_owner, 1)
        self.assertEqual(clone.x, 100.0)
        self.assertEqual(clone.y, 100.0)

        # Move my_ball to simulate movement
        my_ball.x = 200.0
        my_ball.y = 200.0
        clone.x = 50.0
        clone.y = 50.0

        # Test 2: clone exists, should swap
        my_ball.active_skill = "mimic_clone"
        action.execute("use_skill", 0.1)

        self.assertEqual(my_ball.x, 50.0)
        self.assertEqual(my_ball.y, 50.0)
        self.assertEqual(clone.x, 200.0)
        self.assertEqual(clone.y, 200.0)

        clones = [b for b in world.balls if getattr(b, "is_mimic_clone", False)]
        self.assertEqual(len(clones), 1)

if __name__ == '__main__':
    unittest.main()
