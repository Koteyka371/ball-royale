import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FunnyFailsArena

def test_funny_fails_arena_generation():
    arena = FunnyFailsArena(arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 8

    w, h = arena.width, arena.height
    cx, cy = w/2, h/2

    assert arena.rooms[4].x == cx - 100.0
    assert arena.rooms[4].y == cy - 100.0
    assert arena.rooms[4].width == 200.0
    assert arena.rooms[4].height == 200.0
