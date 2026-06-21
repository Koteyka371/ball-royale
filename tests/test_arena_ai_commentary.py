import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import AICommentaryArena

def test_ai_commentary_arena_generation():
    arena = AICommentaryArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1

def test_ai_commentary_arena_is_point_inside():
    arena = AICommentaryArena(arena_size=2000.0, seed=42)

    # Point inside top-left room
    assert arena.is_point_inside(200.0, 200.0, 10.0)

    # Point in the central room (near the hazard, but still in the room)
    assert arena.is_point_inside(arena.width/2, arena.height/2, 10.0)

    # Point in a corridor
    assert arena.is_point_inside(200.0, 500.0, 10.0)

    # Point in the negative space (outside)
    assert not arena.is_point_inside(500.0, 500.0, 10.0)
