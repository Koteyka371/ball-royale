import pytest
from src.arena.arena_types import get_arena, Finals1v1Arena

def test_finals_1v1_arena_generation():
    arena = get_arena("finals_1v1")
    assert isinstance(arena, Finals1v1Arena)
    assert len(arena.rooms) == 1
    assert len(arena.hazards) == 36

    room = arena.rooms[0]
    assert room.width == 400
    assert room.height == 400

    # Hazards should be lava and do 50 damage
    for hazard in arena.hazards:
        assert hazard.kind == "lava"
        assert hazard.damage == 50.0
