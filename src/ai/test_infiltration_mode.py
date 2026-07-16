import unittest
from ai.game_modes import InfiltrationMode

class MockEntity(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockWorld(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

class TestInfiltrationMode(unittest.TestCase):
    def test_setup_and_tick(self):
        mode = InfiltrationMode()
        b1 = MockEntity(id=1, ball_type="player", x=0, y=0, radius=10)
        world = MockWorld(arena=MockEntity(hazards=[]), dead_balls=[])
        mode.setup(world, [b1])
        self.assertEqual(b1.stealth_booster_timer, 9999.0)

        b1.skill_timer = 1.0
        mode.tick(world, [b1], 0.1)
        self.assertTrue(b1.reveal_timer > 0)
        self.assertEqual(b1.stealth_booster_timer, 0.0)

        b1.reveal_timer = 0.0
        b1.last_skill_timer = 1.0
        world.arena.hazards.append(MockEntity(kind="laser_tripwire", x=5, y=5, radius=10))
        mode.tick(world, [b1], 0.1)
        self.assertTrue(world.alarm_triggered)
        self.assertEqual(b1.stealth_booster_timer, 0.0)
