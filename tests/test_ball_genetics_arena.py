import pytest
from arena.arena_types import BallGeneticsArena

def test_ball_genetics_arena_generation():
    arena = BallGeneticsArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()

    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 1

    # Check if dimensions are valid
    for room in arena.rooms:
        assert room.width > 0
        assert room.height > 0
