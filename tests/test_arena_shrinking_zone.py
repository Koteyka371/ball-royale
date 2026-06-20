import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import ShrinkingZoneArena

def test_shrinking_zone_arena_generation():
    arena = ShrinkingZoneArena(arena_size=2000.0)

    assert len(arena.rooms) == 1
    assert len(arena.corridors) == 0
    assert len(arena.hazards) == 0

    room = arena.rooms[0]
    assert room.x == 50.0
    assert room.y == 50.0
    assert room.width == 1900.0
    assert room.height == 1900.0
