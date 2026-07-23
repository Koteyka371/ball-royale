import sys
import unittest
from ai.game_modes import VampiricHazardMode, GAME_MODES
from unittest.mock import MagicMock

class TestVampiricHazardMode(unittest.TestCase):
    def test_mode_exists(self):
        self.assertIn('vampiric_hazard', GAME_MODES)

    def test_hazard_drain_and_heal(self):
        mode = VampiricHazardMode()
        mode.hazard_timer = 0.0 # Force spawn

        world = MagicMock()
        world.arena.width = 1000
        world.arena.height = 1000
        world.arena.hazards = []
        world.events = []
        world.season = 1
        world.leaderboard_manager.data = {'current_season': 1}
        world.profile_manager = world.leaderboard_manager

        def add_event(type, data):
            world.events.append((type, data))
        world.add_event = add_event

        balls = []

        # Ball 1 inside hazard
        b1 = MagicMock()
        b1.id = "b1"
        b1.hp = 100
        b1.max_hp = 100
        b1.x = 500
        b1.y = 500
        b1.team = 1
        balls.append(b1)

        # Ball 2 outside, enemy team
        b2 = MagicMock()
        b2.id = "b2"
        b2.hp = 50
        b2.max_hp = 100
        b2.x = 200
        b2.y = 200
        b2.team = 2
        balls.append(b2)

        # Force hazard spawn at 500,500
        mode.random = MagicMock()
        mode.random.uniform.return_value = 0
        mode.random.randint.return_value = 1000

        # Setup and tick
        mode.setup(world, balls)
        mode.tick(world, balls, 0.1) # Spawn

        self.assertEqual(len(world.arena.hazards), 1)
        h = world.arena.hazards[0]
        self.assertEqual(h.x, 500)
        self.assertEqual(h.y, 500)

        # Next tick should process hazard
        world.events.clear()
        mode.tick(world, balls, 0.1)

        # b1 should lose HP, b2 should gain HP
        self.assertEqual(b1.hp, 98.0) # 100 - (10.0 * 0.1)
        self.assertEqual(b2.hp, 52.0) # 50 + 1.0

        has_damage = any(e[0] == "damage" and e[1]["target"] == "b1" for e in world.events)
        has_heal = any(e[0] == "heal" and e[1]["target"] == "b2" for e in world.events)

        self.assertTrue(has_damage)
        self.assertTrue(has_heal)

if __name__ == '__main__':
    unittest.main()
