import pytest
from arena.arena_types import BodyBlockArena

def test_body_block_arena_generation():
    arena = BodyBlockArena()
    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 1
    assert len(arena.hazards) == 2
