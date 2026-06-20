import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FinalsArena

def test_finals_arena_generation():
    arena = FinalsArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 4

def test_finals_arena_is_point_inside():
    arena = FinalsArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Inside central stage
    assert arena.is_point_inside(cx, cy, 10.0)

    # Inside left spawn area
    assert arena.is_point_inside(cx - 600, cy, 10.0)

    # Inside right spawn area
    assert arena.is_point_inside(cx + 600, cy, 10.0)

    # Outside (top)
    assert not arena.is_point_inside(cx, cy - 500, 10.0)
