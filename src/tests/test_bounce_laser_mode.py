import unittest
from ai.game_modes import BounceLaserMode
from ai.action import Action
from arena.procedural_arena import ProceduralArena

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(2000.0)
        self.balls = []
        self.next_id = 1

class TestBounceLaserMode(unittest.TestCase):
    def test_bounce_laser_mode(self):
        mode = BounceLaserMode()
        world = MockWorld()
        world.tick = 0
        world.arena.hazards = []
        mode.tick(world, [], 5.0)
        # Should have spawned a bounce laser
        has_bounce_laser = any(getattr(h, "kind", "") == "bounce_laser" for h in world.arena.hazards)
        self.assertTrue(has_bounce_laser)

if __name__ == '__main__':
    unittest.main()
