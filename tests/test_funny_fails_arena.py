import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import ARENAS

def test_funny_fails_arena():
    assert "funny_fails" in ARENAS
    arena_cls = ARENAS["funny_fails"]
    arena = arena_cls()
    arena.generate()

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5
