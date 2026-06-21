import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import WaitAndWatchArena

def test_wait_and_watch_arena_generation():
    arena = WaitAndWatchArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5

def test_wait_and_watch_arena_is_point_inside():
    arena = WaitAndWatchArena(arena_size=2000.0, seed=42)
    w, h = arena.width, arena.height
    cx, cy = w/2, h/2

    # Point inside the central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point inside a corner room
    assert arena.is_point_inside(cx - 750, cy - 750, 10.0)

    # Point outside
    assert not arena.is_point_inside(10.0, 10.0, 10.0)
