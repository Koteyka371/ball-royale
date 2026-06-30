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

if __name__ == '__main__':
    unittest.main()
