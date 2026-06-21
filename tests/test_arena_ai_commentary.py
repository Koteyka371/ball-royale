import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from arena.arena_types import get_arena, AICommentaryArena

def test_ai_commentary_arena_generation():
    arena_size = 2000.0
    arena = get_arena("ai_commentary", arena_size=arena_size, seed=42)

    assert isinstance(arena, AICommentaryArena)
    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 3
    assert len(arena.hazards) == 5

    # Center coords
    cx, cy = arena_size / 2, arena_size / 2

    # Check safe broadcasting booth
    booth = next(r for r in arena.rooms if r.width == 200 and r.height == 200)
    assert booth.x == cx - 100
    assert booth.y == cy - 800

    # Check a hazard
    center_lava = next(h for h in arena.hazards if h.id == 0)
    assert center_lava.x == cx
    assert center_lava.y == cy
    assert center_lava.kind == "lava"
    assert center_lava.damage == 25.0

    # Test point inside booth
    assert arena.is_point_inside(cx, cy - 700, 10.0)

    # Test point outside
    assert not arena.is_point_inside(cx - 900, cy - 900, 10.0)
