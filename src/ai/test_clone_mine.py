import unittest
from ai.action import Action
from ai.test_action_advanced import MockBall

class MockWorld:
    def __init__(self):
        self.balls = []
        self._deal_damage_calls = []
        self.width = 1000
        self.height = 1000

    def _deal_damage(self, target, attacker):
        self._deal_damage_calls.append((target, attacker))
        if hasattr(target, "hp"):
            target.hp -= getattr(attacker, "damage", 10)

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if (b.x-ball.x)**2 + (b.y-ball.y)**2 <= radius**2]

class TestCloneMine(unittest.TestCase):
    def test_clone_mine_explosion(self):
        world = MockWorld()

        clone = MockBall(x=50, y=50)
        clone.is_clone = True
        clone.clone_owner = 123
        clone.alive = True
        clone.damage = 0
        clone.team = "team_a"

        enemy = MockBall(x=52, y=52) # Very close
        enemy.alive = True
        enemy.team = "team_b"
        enemy.hp = 100
        enemy.is_illusion = False

        world.balls.extend([clone, enemy])

        action = Action(clone, world)

        # Override _attempt_damage in test since it usually needs a complex attacker/target setup that drops out due to misses
        action._attempt_damage = lambda attacker, target: setattr(target, 'hp', target.hp - attacker.damage)

        action.execute("idle", 0.016)

        self.assertTrue(not getattr(clone, "alive", True))
        self.assertTrue(getattr(enemy, "hp", 100) < 100)


    def test_clone_mine_cascade(self):
        world = MockWorld()

        clone1 = MockBall(x=50, y=50)
        clone1.is_clone = True
        clone1.clone_owner = 123
        clone1.alive = True
        clone1.damage = 0
        clone1.team = "team_a"

        clone2 = MockBall(x=100, y=100) # within aoe_radius (80) distance: 50*sqrt(2) ~ 70.7
        clone2.is_clone = True
        clone2.clone_owner = 123
        clone2.alive = True
        clone2.damage = 0
        clone2.team = "team_a"
        clone2.clone_cascade_timer = -1.0

        enemy = MockBall(x=52, y=52) # Very close to clone1
        enemy.alive = True
        enemy.team = "team_b"
        enemy.hp = 100
        enemy.is_illusion = False

        world.balls.extend([clone1, clone2, enemy])

        action1 = Action(clone1, world)
        action1._attempt_damage = lambda attacker, target: setattr(target, 'hp', target.hp - attacker.damage)

        # Trigger explosion on clone1
        action1.execute("idle", 0.016)

        self.assertFalse(getattr(clone1, "alive", True))
        self.assertTrue(getattr(enemy, "hp", 100) < 100)
        self.assertTrue(getattr(clone2, "clone_cascade_timer", -1.0) > 0)

        action2 = Action(clone2, world)
        action2._attempt_damage = lambda attacker, target: setattr(target, 'hp', target.hp - attacker.damage)

        # wait for cascade to trigger
        action2.execute("idle", 0.26)
        self.assertFalse(getattr(clone2, "alive", True))

if __name__ == '__main__':
    unittest.main()
