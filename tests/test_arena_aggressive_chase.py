import sys
import os

# Ensure src/ is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import AggressiveChaseArena

def test_aggressive_chase_arena_generation():
    arena = AggressiveChaseArena(arena_size=1000.0, seed=42)

    # Check that rooms and corridors were generated
    assert len(arena.rooms) == 5, f"Expected 5 rooms, got {len(arena.rooms)}"
    assert len(arena.corridors) == 4, f"Expected 4 corridors, got {len(arena.corridors)}"

    # Check bounds
    assert arena.width == 1000.0
    assert arena.height == 1000.0
