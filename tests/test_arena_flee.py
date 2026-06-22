import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import ARENAS

def test_flee_arena():
    assert "flee" in ARENAS
    arena_cls = ARENAS["flee"]
    arena = arena_cls(arena_size=2000.0)
    arena.generate()

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1
