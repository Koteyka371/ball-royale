import sys
import os
sys.path.append(os.path.abspath("src"))

from arena.arena_types import ARENAS

def test_funny_fails_arena():
    assert "funny_fails" in ARENAS
    arena_class = ARENAS["funny_fails"]
    arena = arena_class(arena_size=2000.0)
    assert len(arena.rooms) > 0
    assert len(arena.hazards) > 0

if __name__ == "__main__":
    test_funny_fails_arena()
    print("Success")
