import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EscortArena

def test_escort_arena_generation():
    arena = EscortArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 3

def test_escort_arena_is_point_inside():
    arena = EscortArena(arena_size=2000.0, seed=42)
    # Start room point
    assert arena.is_point_inside(150, arena.height/2, 10.0)

    # End room point
    assert arena.is_point_inside(arena.width - 150, arena.height/2, 10.0)
