import pytest
from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    # Check hazards placement
    hazard = arena.hazards[0]
    assert hazard.x == 1000.0
    assert hazard.y == 1000.0
    assert hazard.radius == 150.0
    assert hazard.kind == "lava"
    assert hazard.damage == 25.0
