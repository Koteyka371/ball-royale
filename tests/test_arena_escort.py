import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EscortArena

def test_escort_arena_generation():
    arena = EscortArena(arena_size=2000.0)
    arena.generate()

    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 3

    assert arena.width == 2000.0
    assert arena.height == 2000.0

def test_escort_arena_bounds():
    arena = EscortArena(arena_size=2000.0)
    arena.generate()

    # Start base
    assert arena.is_point_inside(200.0, 1000.0, 10.0)
    # End base
    assert arena.is_point_inside(1800.0, 1000.0, 10.0)
    # Center path
    assert arena.is_point_inside(1000.0, 1000.0, 10.0)
