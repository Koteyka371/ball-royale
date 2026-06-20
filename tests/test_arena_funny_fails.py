import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FunnyFailsArena

def test_funny_fails_arena_generation():
    arena = FunnyFailsArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 1
    assert arena.rooms[0].width == 1900.0
    assert arena.rooms[0].height == 1900.0
    assert len(arena.hazards) == 49
