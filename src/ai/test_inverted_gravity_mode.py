import unittest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

class MockBall:
    def __init__(self, id, x=500, y=500, vx=0, vy=0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.alive = True
        self.hp = 100
        self.ball_type = "normal"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class TestInvertedGravityMode(unittest.TestCase):
    def setUp(self):
        self.mode = GAME_MODES['inverted_gravity']
        self.world = MockWorld()
        self.balls = [
            MockBall(1, y=500, vy=0),
            MockBall(2, y=800, vy=0)
        ]

    def test_setup(self):
        self.mode.setup(self.world, self.balls)
        self.assertFalse(self.mode.gravity_inverted)
        self.assertEqual(self.mode.toggle_timer, 10.0)

    def test_tick_normal_gravity(self):
        self.mode.setup(self.world, self.balls)

        # Test normal gravity (pushing down)
        delta = 1.0
        initial_y = [b.y for b in self.balls]

        self.mode.tick(self.world, self.balls, delta)

        # Should have positive vy (downward)
        for b in self.balls:
            self.assertTrue(b.vy > 0)

    def test_tick_inverted_gravity(self):
        self.mode.setup(self.world, self.balls)
        self.mode.gravity_inverted = True
        self.mode.toggle_timer = 10.0

        # Test inverted gravity (pushing up)
        delta = 1.0

        self.mode.tick(self.world, self.balls, delta)

        # Should have negative vy (upward)
        for b in self.balls:
            self.assertTrue(b.vy < 0)

    def test_boundary_collision_inverted(self):
        self.mode.setup(self.world, self.balls)
        self.mode.gravity_inverted = True

        b = self.balls[0]
        b.y = 5.0 # near top
        b.vy = -100.0 # moving up fast

        self.mode.tick(self.world, self.balls, 1.0)

        self.assertEqual(b.y, b.radius) # clamped to top
        self.assertTrue(b.vy > 0) # bounced back down

    def test_boundary_collision_normal(self):
        self.mode.setup(self.world, self.balls)
        self.mode.gravity_inverted = False

        b = self.balls[0]
        b.y = 995.0 # near bottom
        b.vy = 100.0 # moving down fast

        self.mode.tick(self.world, self.balls, 1.0)

        self.assertEqual(b.y, self.world.arena.height - b.radius) # clamped to bottom
        self.assertTrue(b.vy < 0) # bounced back up

    def test_toggle_logic(self):
        self.mode.setup(self.world, self.balls)
        self.assertFalse(self.mode.gravity_inverted)
        self.mode.toggle_timer = 0.5

        # Tick to toggle
        self.mode.tick(self.world, self.balls, 1.0)

        self.assertTrue(self.mode.gravity_inverted)
        self.assertTrue(self.mode.toggle_timer > 0)
        self.assertTrue(any(e["type"] == "gravity_toggle" for e in self.world.events))

if __name__ == '__main__':
    unittest.main()
