import pytest
from arena.arena_types import get_arena, FinalsArena

def test_finals_arena_generation():
    arena = get_arena("finals", arena_size=2000.0)
    assert isinstance(arena, FinalsArena)
    assert len(arena.rooms) == 1
    assert len(arena.hazards) == 16
    assert all(h.kind == "lava" for h in arena.hazards)
    assert arena.rooms[0].width == 800
    assert arena.rooms[0].height == 800
