import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import get_arena, TargetWeakArena

def test_target_weak_arena():
    arena = get_arena("target_weak", arena_size=2000)
    assert isinstance(arena, TargetWeakArena)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 4

if __name__ == "__main__":
    test_target_weak_arena()
    print("Test passed!")
