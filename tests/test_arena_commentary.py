import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import CommentaryArena

def test_commentary_arena_generation():
    arena = CommentaryArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

def test_commentary_arena_is_point_inside():
    arena = CommentaryArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point inside the central arena
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point inside top-left commentator booth
    assert arena.is_point_inside(cx - 450, cy - 450, 10.0)

    # Point outside
    assert not arena.is_point_inside(10, 10, 10.0)
