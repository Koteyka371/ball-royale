import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EscortArena

def test_escort_arena_generation():
    arena = EscortArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 5

    # Check safe zones
    assert arena.rooms[0].width == 200
    assert arena.rooms[0].height == 200

    assert arena.rooms[1].width == 200
    assert arena.rooms[1].height == 200

def test_escort_arena_is_point_inside():
    arena = EscortArena(arena_size=2000.0, seed=42)

    # Point in the first room (start safe zone)
    assert arena.is_point_inside(100, 100, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
