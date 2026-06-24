import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import BlackHoleArena

def test_black_hole_arena_generation():
    arena = BlackHoleArena(arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1
    assert arena.hazards[0].kind == "black_hole"

def test_black_hole_arena_is_point_inside():
    arena = BlackHoleArena(arena_size=2000.0)
    assert arena.is_point_inside(1000.0, 1000.0, 10.0)
    assert arena.is_point_inside(100.0, 100.0, 10.0)
