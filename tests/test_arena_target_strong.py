import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=1000.0, seed=42)
    arena.generate()
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1
