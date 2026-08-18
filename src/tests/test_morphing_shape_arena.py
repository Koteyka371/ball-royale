import unittest
import math
from unittest.mock import MagicMock
from arena.arena_types import MorphingShapeArena
from ai.game_modes import MorphingShapeArenaMode

class TestMorphingShapeArena(unittest.TestCase):
    def test_morphing_arena_initialization(self):
        arena = MorphingShapeArena(2000.0)
        self.assertEqual(arena.width, 2000.0)
        self.assertEqual(arena.current_shape_idx, 0)
        self.assertFalse(arena.is_morphing)

    def test_update_triggers_morph(self):
        arena = MorphingShapeArena(2000.0)
        arena.update_zone(3600, 1.0)
        self.assertTrue(arena.is_morphing)
        self.assertEqual(arena.morph_timer, 1.0)

        # update slightly to morph
        arena.update_zone(3601, 1.0)
        self.assertEqual(arena.morph_timer, 2.0)

        # finish morph
        arena.update_zone(3602, 5.0)
        self.assertFalse(arena.is_morphing)
        self.assertEqual(arena.current_shape_idx, 1) # square -> circle

    def test_clamping_morph(self):
        arena = MorphingShapeArena(2000.0)

        # initially square
        cx, cy = arena.cx, arena.cy
        # point outside the square should be clamped
        # square max is cx + 0.45 * width = 1000 + 900 = 1900
        x, y, bounced = arena.clamp_position(1950, 1000, 10.0)
        self.assertTrue(bounced)
        self.assertLessEqual(x, 1900)

        # morph to circle
        arena.current_shape_idx = 1
        x, y, bounced = arena.clamp_position(1900, 1900, 10.0) # corners are outside circle
        self.assertTrue(bounced)

    def test_game_mode_setup(self):
        mode = MorphingShapeArenaMode()
        world = type('MockWorld', (), {})()
        world.arena = MagicMock()
        world.arena.width = 2000.0

        mode.setup(world, [])
        self.assertIsInstance(world.arena, MorphingShapeArena)
