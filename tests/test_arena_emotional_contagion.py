import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena():
    arena = EmotionalContagionArena(arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1

    # check hazard
    hazard = arena.hazards[0]
    assert hazard.kind == "lava"
    assert hazard.radius == 80.0
    assert hazard.damage == 20.0
