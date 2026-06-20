import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FunnyFailsArena

def test_funny_fails_arena_generation():
    arena = FunnyFailsArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 8

def test_funny_fails_arena_is_point_inside():
    arena = FunnyFailsArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point inside the tiny central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point inside top-left corner room
    assert arena.is_point_inside(200, 200, 10.0)

    # Point on narrow corridor
    assert arena.is_point_inside(cx, 300, 5.0)

    # Point outside (in a hazard)
    assert not arena.is_point_inside(cx - 150, cy - 150, 10.0)

def test_funny_fails_hazards_are_lava():
    arena = FunnyFailsArena(arena_size=2000.0, seed=42)
    for hazard in arena.hazards:
        assert hazard.kind == "lava"
        assert hazard.damage == 50.0
