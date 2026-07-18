import unittest
import math
from arena.arena_types import ShiftingBoundariesArena
from arena.procedural_arena import Room

class TestShiftingBoundariesArena(unittest.TestCase):
    def test_initialization(self):
        arena = ShiftingBoundariesArena(2000.0)
        self.assertEqual(arena.min_x, 0.0)
        self.assertEqual(arena.min_y, 0.0)
        self.assertEqual(arena.max_x, 2000.0)
        self.assertEqual(arena.max_y, 2000.0)

    def test_update_zone_shifts_boundaries(self):
        arena = ShiftingBoundariesArena(2000.0)
        arena.target_min_x = 500.0
        arena.target_min_y = 500.0
        arena.target_max_x = 1500.0
        arena.target_max_y = 1500.0
        arena.shift_speed = 100.0
        arena.update_zone(1, 1.0)
        self.assertEqual(arena.min_x, 100.0)
        self.assertEqual(arena.min_y, 100.0)
        self.assertEqual(arena.max_x, 1900.0)
        self.assertEqual(arena.max_y, 1900.0)

    def test_clamp_position(self):
        arena = ShiftingBoundariesArena(2000.0)
        arena.min_x = 500.0
        arena.max_x = 1500.0
        arena.min_y = 500.0
        arena.max_y = 1500.0

        # Test ProceduralArena clamping logic compatibility (must set safe zone correctly to not bounce inside bounds)
        arena.safe_zone_radius = 5000.0 # Make safe zone huge so procedural clamp doesn't interfere
        arena.safe_zone_center = (1000.0, 1000.0)
        arena.rooms.clear()
        arena.corridors.clear()
        arena.rooms.append(Room(0, 0, 2000, 2000))

        # Within boundaries
        x, y, bounced = arena.clamp_position(1000.0, 1000.0, 10.0)
        self.assertFalse(bounced)

        # OOB
        x, y, bounced = arena.clamp_position(100.0, 100.0, 10.0)
        self.assertTrue(bounced)
        self.assertGreaterEqual(x, 510.0)
        self.assertGreaterEqual(y, 510.0)
