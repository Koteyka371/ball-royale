import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 1
    assert len(arena.hazards) == 4
    for hazard in arena.hazards:
        assert hazard.kind == "lava"
        assert hazard.damage == 100.0
