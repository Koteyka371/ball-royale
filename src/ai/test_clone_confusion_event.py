import unittest
import copy

from ai.game_modes import GAME_MODES, CloneConfusionEventMode

class MockWorld:
    def __init__(self):
        self.next_id = 200
        self.balls = []
        self.damage_dealt = []

    def _deal_damage(self, attacker, target, amount):
        self.damage_dealt.append((attacker, target, amount))
        if isinstance(target, dict):
            target["hp"] -= amount
        else:
            target.hp -= amount


class MockBall:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, "experience"):
            self.experience = 0.0

class TestCloneConfusionEventMode(unittest.TestCase):
    def test_clone_confusion_setup(self):
        mode = CloneConfusionEventMode()
        world = MockWorld()

        player = MockBall(**{
            "id": 1,
            "hp": 100,
            "alive": True,
            "ball_type": "player",
            "is_decoy": False,
            "is_illusion": False,
            "skill": "fireball",
            "active_skill": "active",
            "brain": "brain"
        })
        world.balls.append(player)

        mode.setup(world, world.balls)

        self.assertEqual(len(world.balls), 2)
        clone = world.balls[1]

        self.assertEqual(getattr(clone, "clone_confusion_owner_id"), 1)
        self.assertTrue(getattr(clone, "is_decoy"))
        self.assertTrue(getattr(clone, "is_illusion"))
        self.assertEqual(getattr(clone, "decoy_timer"), 10.0)
        self.assertEqual(getattr(clone, "illusion_timer"), 10.0)

        self.assertIsNone(getattr(clone, "skill"))
        self.assertIsNone(getattr(clone, "active_skill"))
        self.assertIsNone(getattr(clone, "brain"))
        self.assertEqual(getattr(clone, "id"), 200)

    def test_clone_confusion_tick(self):
        mode = CloneConfusionEventMode()
        world = MockWorld()

        player = MockBall(**{
            "id": 1,
            "hp": 100,
            "alive": True,
            "ball_type": "player",
            "x": 50,
            "y": 50,
            "vx": 10,
            "vy": 20,
            "target_x": 60,
            "target_y": 70,
        })
        world.balls.append(player)
        mode.setup(world, world.balls)
        clone = world.balls[1]

        mode.tick(world, world.balls, 0.1)

        # Clone should have mirrored velocity and targets
        self.assertEqual(getattr(clone, "vx"), -10)
        self.assertEqual(getattr(clone, "vy"), -20)
        self.assertEqual(getattr(clone, "target_x"), 40)
        self.assertEqual(getattr(clone, "target_y"), 30)

        # Apply damage to the clone
        clone.hp -= 30

        mode.tick(world, world.balls, 0.1)

        # The damage should redirect to the player
        self.assertEqual(len(world.damage_dealt), 1)
        _, target, amount = world.damage_dealt[0]
        self.assertEqual(getattr(target, "id"), 1)
        self.assertEqual(amount, 30)
        self.assertEqual(getattr(player, "hp"), 70)

if __name__ == '__main__':
    unittest.main()
