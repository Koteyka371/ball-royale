import unittest
from unittest.mock import MagicMock
from ai.game_modes import OrbitalCrosshairMode

class TestOrbitalCrosshair(unittest.TestCase):
    def test_orbital_crosshair(self):
        mode = OrbitalCrosshairMode()
        world = MagicMock()
        world.arena = MagicMock()
        world.arena.hazards = []
        world.next_id = 1
        world.season = 1
        world.leaderboard_manager = MagicMock()
        world.leaderboard_manager.data = {"matches_played": 0}

        b1 = MagicMock()
        b1.id = 1
        b1.alive = True
        b1.ball_type = "player"
        b1.score = 50
        b1.x = 200
        b1.y = 200
        b1.stamina = 100
        b1.hp = 100
        b1.base_speed_multiplier = 1.0
        b1.speed_multiplier = 1.0

        b2 = MagicMock()
        b2.id = 2
        b2.alive = True
        b2.ball_type = "player"
        b2.score = 100
        b2.x = 300
        b2.y = 300
        b2.stamina = 100
        b2.hp = 100
        b2.base_speed_multiplier = 1.0
        b2.speed_multiplier = 1.0

        balls = [b1, b2]
        mode.setup(world, balls)

        # Test crosshair spawn timer
        mode.tick(world, balls, 5.1)
        self.assertEqual(len(mode.crosshairs), 1)
        self.assertEqual(mode.crosshairs[0]["target_id"], b2.id)

        # Move crosshair close to target
        mode.crosshairs[0]["x"] = 300
        mode.crosshairs[0]["y"] = 300

        mode.spawn_timer = 20.0
        # Test lock on
        mode.tick(world, balls, 2.1)
        self.assertEqual(mode.crosshairs[0]["state"], "locking")

        mode.spawn_timer = 20.0
        # Test firing
        mode.tick(world, balls, 3.1)
        self.assertEqual(len(mode.crosshairs), 0)
        self.assertEqual(len(world.arena.hazards), 1)
        h = world.arena.hazards[0]
        self.assertEqual(h.kind, "irradiated_zone")
        self.assertEqual(h.x, 300)
        self.assertEqual(h.y, 300)

        b2.stamina = 100.0
        mode.spawn_timer = 20.0
        # Test hazard effect on b2
        mode.tick(world, balls, 1.0)
        # Check if hp drained
        b2.take_damage.assert_called_with(10.0, source="irradiated_zone")
        self.assertEqual(b2.stamina, 80.0)
        self.assertEqual(b2.speed_multiplier, 0.5)

if __name__ == "__main__":
    unittest.main()
