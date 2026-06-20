import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import AvoidTrapArena

def test_avoid_trap_arena_generation():
    arena = AvoidTrapArena(arena_size=1000.0, seed=42)
    assert len(arena.rooms) == 2, "Should have 2 safe zone rooms"
    assert len(arena.corridors) == 1, "Should have 1 connecting corridor"
    assert len(arena.hazards) == 15, "Should have exactly 15 hazards generated"

    for hazard in arena.hazards:
        assert hazard.kind == "lava"
        assert hazard.radius == 15.0
        assert hazard.damage == 40.0
