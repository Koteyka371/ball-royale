import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import WaitAndWatchArena

def test_wait_and_watch_arena_generation():
    arena = WaitAndWatchArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5

    # Center room
    assert arena.rooms[0].width == 600.0
    assert arena.rooms[0].height == 600.0

    # Top room
    assert arena.rooms[1].width == 300.0
    assert arena.rooms[1].height == 200.0
