import unittest
import math

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
        self.dead_balls = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0

class TestAuraBombEventMode(unittest.TestCase):
    def test_aura_bomb_logic(self):
        import sys
        sys.path.append('src')
        from ai.game_modes import AuraBombEventMode

        mode = AuraBombEventMode()
        world = MockWorld()
        balls = [MockBall(1, 100, 100), MockBall(2, 100, 150), MockBall(3, 500, 500)]

        mode.event_timer = 15.0
        mode.tick(world, balls, delta=0.016)

        bombed_balls = [b for b in balls if getattr(b, "has_aura_bomb", False)]
        self.assertTrue(len(bombed_balls) >= 1)

        b1 = bombed_balls[0]
        self.assertTrue(getattr(b1, "aura_bomb_timer", 0) > 0)

        for _ in range(6):
            mode.tick(world, balls, delta=1.0)

        self.assertFalse(getattr(b1, "has_aura_bomb", False))
        self.assertTrue(any(e[0] == "aura_bomb_exploded" for e in world.events))

if __name__ == '__main__':
    unittest.main()
