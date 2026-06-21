import pytest
from src.arena.arena_types import get_arena, FunnyFailsArena

def test_funny_fails_arena():
    arena = get_arena("funny_fails", arena_size=2000)
    assert isinstance(arena, FunnyFailsArena)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

if __name__ == "__main__":
    test_funny_fails_arena()
    print("Test passed!")
