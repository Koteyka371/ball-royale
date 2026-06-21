import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena_generation():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 8

    # Check hazards exist and have expected properties
    spikes = [h for h in arena.hazards if h.kind == "spikes"]
    lava = [h for h in arena.hazards if h.kind == "lava"]
    assert len(spikes) == 4
    assert len(lava) == 4
