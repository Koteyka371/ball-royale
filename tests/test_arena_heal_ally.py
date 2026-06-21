import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import HealAllyArena

def test_heal_ally_arena():
    arena = HealAllyArena(arena_size=2000.0)
    arena.generate()
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5
    assert arena.hazards[0].kind == "spikes"
