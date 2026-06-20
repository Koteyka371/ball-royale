import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import AmbushArena

def test_ambush_arena_generation():
    arena = AmbushArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 9 # 1 central + 8 small rooms
    assert len(arena.corridors) == 8 # 8 corridors connecting

    # Central room
    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

    # Hiding spot rooms
    for room in arena.rooms[1:]:
        assert room.width == 100
        assert room.height == 100

def test_ambush_arena_is_point_inside():
    arena = AmbushArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in top-left hiding spot
    assert arena.is_point_inside(cx - 350, cy - 350, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
