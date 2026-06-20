import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0)
    arena.generate()

    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 1
    assert len(arena.hazards) == 1

    hazard = arena.hazards[0]
    assert hazard.kind == "spikes"
    assert hazard.damage == 30.0
