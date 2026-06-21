import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EscortArena, get_arena

def test_escort_arena_generation():
    arena = EscortArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()

    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 1
    assert len(arena.hazards) == 6

def test_get_escort_arena():
    arena = get_arena("escort")
    assert isinstance(arena, EscortArena)
