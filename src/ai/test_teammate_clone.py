import unittest
from ai.action import Action

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.damage = 10.0
        self.skill = "teammate_clone"
        self.team = "red"
        self.name = "MyBall"
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

class TestTeammateClone(unittest.TestCase):
    def test_teammate_clone_with_teammate(self):
        world = MockWorld()

        my_ball = MockBall(id=1, x=100.0, y=100.0)
        world.balls.append(my_ball)

        teammate = MockBall(id=2, x=200.0, y=200.0, name="TeammateBall")
        world.balls.append(teammate)

        action = Action(my_ball, world)
        my_ball.active_skill = "teammate_clone"
        action.execute("use_skill", 0.1)

        clones = [b for b in world.balls if getattr(b, "is_decoy_clone", False)]
        self.assertEqual(len(clones), 1)
        clone = clones[0]

        self.assertEqual(clone.mimic_owner, 1)
        self.assertEqual(clone.x, 100.0)
        self.assertEqual(clone.y, 100.0)
        self.assertEqual(clone.name, "TeammateBall")
        self.assertEqual(clone.hp, 50.0)
        self.assertEqual(clone.damage, 0.0)
        self.assertEqual(clone.skill, None)

    def test_teammate_clone_no_teammate(self):
        world = MockWorld()

        my_ball = MockBall(id=1, x=100.0, y=100.0, name="MyBall")
        world.balls.append(my_ball)

        action = Action(my_ball, world)
        my_ball.active_skill = "teammate_clone"
        action.execute("use_skill", 0.1)

        clones = [b for b in world.balls if getattr(b, "is_decoy_clone", False)]
        self.assertEqual(len(clones), 1)
        clone = clones[0]

        self.assertEqual(clone.mimic_owner, 1)
        self.assertEqual(clone.name, "MyBall")

if __name__ == '__main__':
    unittest.main()
