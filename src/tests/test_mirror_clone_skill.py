import unittest
from ai.action import Action

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 200.0
        self.y = 300.0
        self.vx = 10.0
        self.vy = 20.0
        self.hp = 100.0
        self.alive = True
        self.damage = 10.0
        self.skill = "mirror_clone"
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius=0):
        return (x, y, False)

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = MockArena()
        self.next_id = 9999

class TestMirrorCloneSkill(unittest.TestCase):
    def test_mirror_clone_creation_and_movement(self):
        world = MockWorld()

        my_ball = MockBall(id=1, x=200.0, y=300.0)
        world.balls.append(my_ball)

        action = Action(my_ball, world)
        my_ball.active_skill = "mirror_clone"
        action.execute("use_skill", 0.1)

        clones = [b for b in world.balls if getattr(b, "is_mirror_clone", False)]
        self.assertEqual(len(clones), 1)
        clone = clones[0]
        self.assertEqual(clone.mirror_clone_owner, 1)

        # Initial position mirrored
        self.assertEqual(clone.x, 800.0)
        self.assertEqual(clone.y, 700.0)

        # Move my_ball to simulate movement
        my_ball.x = 250.0
        my_ball.y = 350.0
        my_ball.vx = 50.0
        my_ball.vy = -10.0

        clone_action = Action(clone, world)
        clone_action.execute("idle", 0.1)

        # Clone should track mirrored position of owner
        self.assertEqual(clone.x, 750.0)
        self.assertEqual(clone.y, 650.0)
        # Velocity should be inverted
        self.assertEqual(clone.vx, -50.0)
        self.assertEqual(clone.vy, 10.0)

if __name__ == '__main__':
    unittest.main()
