import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import CircleStrafeArena

def test_circle_strafe_arena_generation():
    arena = CircleStrafeArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 4

def test_circle_strafe_arena_is_point_inside():
    arena = CircleStrafeArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in top corridor
    assert arena.is_point_inside(cx, cy - 300, 10.0)

    # Point in top-left room
    assert arena.is_point_inside(cx - 250, cy - 250, 10.0)

    # Point in central hole
    assert not arena.is_point_inside(cx, cy, 10.0)
