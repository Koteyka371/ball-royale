import pytest
from arena.arena_types import get_arena, TargetWeakArena

def test_target_weak_arena():
    arena = get_arena("target_weak", arena_size=2000.0)
    assert isinstance(arena, TargetWeakArena)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4
