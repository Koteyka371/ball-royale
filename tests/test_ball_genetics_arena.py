import pytest
from arena.arena_types import get_arena, BallGeneticsArena

def test_ball_genetics_arena_generation():
    arena = get_arena("ball_genetics", arena_size=2000.0)
    assert isinstance(arena, BallGeneticsArena)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

    # Verify central room dimensions
    center_room = arena.rooms[0]
    assert center_room.width == 400
    assert center_room.height == 400
    assert center_room.x == 800
    assert center_room.y == 800

    # Verify a hazard location
    top_hazard = arena.hazards[0]
    assert top_hazard.x == 1000
    assert top_hazard.y == 200
    assert top_hazard.kind == "lava"
    assert top_hazard.damage == 10.0
