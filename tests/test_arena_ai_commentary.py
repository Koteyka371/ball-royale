import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import AICommentaryArena

def test_ai_commentary_arena_generation():
    arena = AICommentaryArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5

def test_ai_commentary_arena_is_point_inside():
    arena = AICommentaryArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    assert arena.is_point_inside(cx, cy, 10.0)
    assert arena.is_point_inside(cx, 175, 10.0)
    assert not arena.is_point_inside(10, 10, 10.0)
