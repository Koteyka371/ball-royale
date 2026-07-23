import unittest
from src.ai.game_modes import LavaFountainsEventMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.alive = True
        self.hp = 100

class TestLavaFountainsEventMode(unittest.TestCase):
    def test_lava_fountains_event(self):
        mode = LavaFountainsEventMode()
        world = MockWorld()
        balls = [MockBall(100, 100)]

        # Loop until event triggers
        import random
        random.seed(42) # Set seed for predictability
        for _ in range(100):
            mode.event_timer = 21.0
            mode.tick(world, balls, delta=0.0)
            if mode.event_active:
                break

        self.assertTrue(mode.event_active)

        # Force a fountain to spawn
        mode.fountain_spawn_timer = 0
        mode.event_duration = 10.0
        mode.tick(world, balls, delta=0.1)
        self.assertTrue(len(world.arena.hazards) > 0)

        fountain = world.arena.hazards[0]
        self.assertEqual(fountain.kind, "lava_fountain")

        # Advance time to turn fountain into puddle
        mode.tick(world, balls, delta=2.1)

        self.assertEqual(fountain.kind, "lava_puddle")

        balls[0].x = fountain.x
        balls[0].y = fountain.y

        mode.tick(world, balls, delta=1.0)
        self.assertTrue(balls[0].hp < 100) # took damage

if __name__ == '__main__':
    unittest.main()
