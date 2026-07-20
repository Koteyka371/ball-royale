import unittest
from unittest.mock import MagicMock
from ai.game_modes import ZeroGMeteorShowerMode

class MockBall:
    def __init__(self, x=500.0, y=500.0):
        self.x = x
        self.y = y
        self.hp = 1000.0
        self.alive = True
        self.radius = 15.0
        self.vx = 0.0
        self.vy = 0.0
        self.ball_type = "normal"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 500.0
        self.invisible = False

class TestZeroGMeteorShowerMode(unittest.TestCase):
    def test_bouncing_meteors(self):
        mode = ZeroGMeteorShowerMode()
        mode.is_zero_g = True

        world = MagicMock()
        world.arena.width = 1000.0
        world.arena.height = 1000.0
        world.arena.weather = ""
        world.weekly_mutator = ""
        world.mutators_active = False
        world.mutators = []

        ball = MockBall(x=500.0, y=500.0)
        balls = [ball]

        # Add a meteor ready to bounce
        mode.active_meteors.append({
            "id": "test_meteor",
            "x": 500.0,
            "y": 480.0,
            "delay": 0.0, # Will trigger bounce state transition if not already bouncing
            "radius": 30.0,
            "bouncing": False,
            "vx": 0.0,
            "vy": 0.0
        })

        # Initial tick transitions it to bouncing
        mode.tick(world, balls, delta=0.016)
        self.assertTrue(mode.active_meteors[0]["bouncing"])

        # Force a specific trajectory
        mode.active_meteors[0]["vx"] = 0.0
        mode.active_meteors[0]["vy"] = 100.0
        mode.active_meteors[0]["x"] = 500.0
        mode.active_meteors[0]["y"] = 490.0 # Just 10 units away from ball

        initial_hp = ball.hp
        initial_y = ball.y

        mode.tick(world, balls, delta=0.016)

        # Meteor should have moved down (vy * delta) = 1.6 units
        self.assertAlmostEqual(mode.active_meteors[0]["y"], 491.6)

        # Ball should have taken knockback and damage (since dist < 30 + 15)
        self.assertTrue(ball.y > initial_y) # Knockback pushing away
        self.assertTrue(ball.hp < initial_hp) # Damage dealt

    def test_normal_gravity_craters(self):
        mode = ZeroGMeteorShowerMode()
        mode.is_zero_g = False

        world = MagicMock()
        world.arena.width = 1000.0
        world.arena.height = 1000.0
        world.arena.weather = ""
        world.weekly_mutator = ""
        world.mutators_active = False
        world.mutators = []

        ball = MockBall(x=500.0, y=500.0)
        balls = [ball]

        # Add a meteor ready to crash
        mode.active_meteors.append({
            "id": "test_meteor_2",
            "x": 500.0,
            "y": 500.0,
            "delay": -0.1, # Trigger crater creation
            "radius": 30.0,
            "bouncing": False,
            "vx": 0.0,
            "vy": 0.0
        })

        initial_hp = ball.hp

        mode.tick(world, balls, delta=0.016)

        # Meteor should have been removed and turned into a crater
        self.assertEqual(len(mode.active_meteors), 0)
        self.assertEqual(len(mode.craters), 1)
        self.assertEqual(mode.craters[0]["x"], 500.0)

        # Ball should have taken crater impact damage
        self.assertTrue(ball.hp < initial_hp)

if __name__ == '__main__':
    unittest.main()
