import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from arena.arena_types import TargetWeakArena

def test_target_weak_arena_generation():
    arena = TargetWeakArena(arena_size=2000.0)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1
