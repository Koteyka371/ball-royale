import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import get_arena

def test_genetics_arena_generation():
    arena = get_arena("genetics", arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 12

    # The first room is the central large area
    assert arena.rooms[0].width == 800
    assert arena.rooms[0].height == 800

    # The other four are small incubation chambers
    for room in arena.rooms[1:]:
        assert room.width == 200
        assert room.height == 200

def test_genetics_arena_is_point_inside():
    arena = get_arena("genetics", arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in one of the incubation chambers
    assert arena.is_point_inside(100, 100, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
