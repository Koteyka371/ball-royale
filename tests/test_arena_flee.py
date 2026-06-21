import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1
    w, h = arena.width, arena.height
    assert arena.hazards[0].x == w / 2
    assert arena.hazards[0].y == h / 2
