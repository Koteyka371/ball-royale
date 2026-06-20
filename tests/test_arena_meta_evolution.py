import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import MetaEvolutionArena

def test_meta_evolution_arena_generation():
    arena = MetaEvolutionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

    assert arena.rooms[0].width == 300
    assert arena.rooms[1].width == 200

    assert arena.hazards[0].radius == 50.0
    assert arena.hazards[0].kind == "spikes"
    assert arena.hazards[0].damage == 20.0
