import unittest

# Dummy mock object
class MockEntity:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class MockWorld:
    def __init__(self):
        self.entities = []

    def get_nearby_entities(self, target, radius):
        return {"enemies": self.entities}

class TestReflector(unittest.TestCase):
    def test_reflector_take_damage_immune(self):
        from ai.ball_types_reflector import Reflector
        r = Reflector(1, 0, 0)
        r.use_skill()
        r.take_damage(50)
        self.assertEqual(r.hp, r.max_hp)

    def test_action_reflection(self):
        from ai.action import Action
        world = MockWorld()

        target = MockEntity(id=1, x=0, y=0, is_reflective=True, team="red", ball_type="reflector", alive=True)
        attacker = MockEntity(id=2, x=100, y=0, team="blue", is_projectile=True, vx=-100, vy=0)

        enemy = MockEntity(id=3, x=0, y=100, alive=True, team="blue")
        world.entities = [enemy]

        action = Action(target, world)
        action._attempt_damage(attacker, target)

        # Should reflect towards enemy at (0, 100)
        self.assertEqual(attacker.team, "red")
        self.assertEqual(getattr(attacker, "owner_id", None), 1)

        # original speed was 100
        self.assertEqual(attacker.vx, 0)
        self.assertEqual(attacker.vy, 100)

if __name__ == '__main__':
    unittest.main()
