import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EscortArena

def test_escort_arena_generation():
    arena = EscortArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 3
    assert len(arena.hazards) == 3

def test_escort_arena_is_point_inside():
    arena = EscortArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Inside start room
    assert arena.is_point_inside(250, 250, 10.0)

    # Inside end room
    assert arena.is_point_inside(1750, 1750, 10.0)

    # Inside central corridor
    assert arena.is_point_inside(1000, 1000, 10.0)

    # Outside
    assert not arena.is_point_inside(10, 10, 10.0)
