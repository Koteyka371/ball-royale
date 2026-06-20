import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import SwarmArena

def test_swarm_arena_generation():
    arena = SwarmArena(arena_size=2000.0)
    arena.generate()
    assert len(arena.rooms) > 0
    assert len(arena.corridors) > 0
    assert len(arena.hazards) > 0
