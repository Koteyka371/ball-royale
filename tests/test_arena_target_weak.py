import sys
import os

# Ensure src/ is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TargetWeakArena

def test_target_weak_arena_generation():
    arena = TargetWeakArena(arena_size=1000.0, seed=42)

    # Check that rooms, corridors and hazards were generated
    assert len(arena.rooms) == 5, f"Expected 5 rooms, got {len(arena.rooms)}"
    assert len(arena.corridors) == 8, f"Expected 8 corridors, got {len(arena.corridors)}"
    assert len(arena.hazards) == 4, f"Expected 4 hazards, got {len(arena.hazards)}"

    # Check bounds
    assert arena.width == 1000.0
    assert arena.height == 1000.0
