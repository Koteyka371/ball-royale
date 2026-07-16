import unittest
from ai.game_modes import HalfLifeReviveMode

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.base_damage_multiplier = 1.0
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.next_id = 9999
        self.events = []
    def add_event(self, event_type, data):
        self.events.append(data)

class TestHalfLifeReviveMode(unittest.TestCase):
    def test_setup_and_revive(self):
        world = MockWorld()
        b1 = MockBall(id=1, x=100.0, y=100.0)
        world.balls.append(b1)
        mode = HalfLifeReviveMode()

        mode.setup(world, world.balls)

        # Check clone created
        clones = [b for b in world.balls if getattr(b, "is_revive_clone", False)]
        self.assertEqual(len(clones), 1)
        clone = clones[0]
        self.assertEqual(clone.clone_owner, 1)
        self.assertEqual(clone.base_damage_multiplier, 0.5)

        # Simulate double damage
        clone.hp = 80.0
        mode.tick(world, world.balls, 0.1)
        self.assertEqual(clone.hp, 60.0)

        # Simulate player death
        b1.alive = False
        b1.hp = 0
        mode.tick(world, world.balls, 0.1)

        # Verify swap
        self.assertEqual(b1.alive, True)
        self.assertEqual(b1.hp, 50.0)
        self.assertEqual(b1.max_hp, 50.0)
        self.assertEqual(b1.base_damage_multiplier, 0.5)
        self.assertEqual(clone.alive, False)

        # Test input mirroring (vx, vy, skills)
        b2 = MockBall(id=2, x=100.0, y=100.0, vx=10.0, vy=-5.0, active_skill="dash", skill="dash")
        world.balls.append(b2)
        world.dead_players_processed = [] # Reset for b2
        mode.setup(world, world.balls)

        mode.tick(world, world.balls, 0.1)
        clones = [b for b in world.balls if getattr(b, "is_revive_clone", False) and getattr(b, "clone_owner", -1) == 2]
        self.assertEqual(len(clones), 1)
        clone2 = clones[0]
        self.assertEqual(clone2.vx, 10.0)
        self.assertEqual(clone2.vy, -5.0)
        self.assertEqual(clone2.active_skill, "dash")
        self.assertEqual(clone2.skill, "dash")

if __name__ == '__main__':
    unittest.main()
