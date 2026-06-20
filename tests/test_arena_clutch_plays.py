import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import ClutchPlaysArena

def test_clutch_plays_arena_generation():
    arena = ClutchPlaysArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5

def test_clutch_plays_arena_is_point_inside():
    arena = ClutchPlaysArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point inside the central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point inside the top-left safe zone
    assert arena.is_point_inside(200, 200, 10.0)

    # Point outside
    assert not arena.is_point_inside(10, 10, 10.0)
