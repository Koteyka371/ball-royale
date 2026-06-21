import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from arena.arena_types import AICommentaryArena

def test_ai_commentary_arena_generation():
    arena = AICommentaryArena(arena_size=2000.0, seed=42)
    arena.generate()

    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    assert arena.hazards[0].radius == 200.0

def test_ai_commentary_arena_is_point_inside():
    arena = AICommentaryArena(arena_size=2000.0, seed=42)
    arena.generate()
    w, h = arena.width, arena.height

    # Point inside top-left room
    assert arena.is_point_inside(200.0, 200.0, 10.0)

    # Point in left corridor
    assert arena.is_point_inside(300.0, 600.0, 10.0)

    # Point outside (center, dodging hazard)
    assert not arena.is_point_inside(w/2 - 300, h/2, 10.0)
