import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena_generation():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 6
    assert len(arena.corridors) == 0

    # Test the horizontal strips
    assert arena.rooms[0].width == 1800
    assert arena.rooms[0].height == 300

    # Test the vertical strips
    assert arena.rooms[3].width == 300
    assert arena.rooms[3].height == 1800

def test_emotional_contagion_arena_is_point_inside():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room (overlap of center horizontal and center vertical strips)
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in the empty negative space "pillars" (e.g., between the strips)
    # The first horizontal strip is y=100..400.
    # The middle horizontal strip is cy-150..cy+150 (850..1150)
    # The first vertical strip is x=100..400.
    # The middle vertical strip is cx-150..cx+150 (850..1150)
    # A point between first H strip and middle H strip, and between first V strip and middle V strip
    # e.g., x=600, y=600 should be outside.
    assert not arena.is_point_inside(600, 600, 10.0)

    # Another negative space between middle and last strips
    assert not arena.is_point_inside(1400, 1400, 10.0)
