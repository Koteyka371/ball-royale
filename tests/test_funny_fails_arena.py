import pytest
from arena.arena_types import FunnyFailsArena

def test_funny_fails_arena_generation():
    arena = FunnyFailsArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()

    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 9
    assert len(arena.hazards) == 5

    assert arena.hazards[0].kind == "lava"
