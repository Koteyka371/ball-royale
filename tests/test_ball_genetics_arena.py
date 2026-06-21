import pytest
from arena.arena_types import BallGeneticsArena

def test_ball_genetics_arena():
    arena = BallGeneticsArena(arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5
