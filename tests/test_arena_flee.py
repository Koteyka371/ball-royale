import pytest
from src.arena.arena_types import FleeArena

def test_flee_arena():
    arena = FleeArena(arena_size=2000.0, num_rooms=5, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    assert arena.hazards[0].kind == "lava"
    assert arena.hazards[0].radius == 80.0
