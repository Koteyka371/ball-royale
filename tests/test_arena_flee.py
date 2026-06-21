import sys
import os

# Ensure src/ is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=1000.0, seed=42)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5

    assert arena.width == 1000.0
    assert arena.height == 1000.0
