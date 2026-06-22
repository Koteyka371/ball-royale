import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 1
    assert arena.width == 2000.0
    assert arena.height == 2000.0
