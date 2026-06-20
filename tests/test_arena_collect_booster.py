import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import CollectBoosterArena

def test_collect_booster_arena_generation():
    arena = CollectBoosterArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8

    # The first room is the central one
    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

    # The other four are corner rooms
    for room in arena.rooms[1:]:
        assert room.width == 150
        assert room.height == 150

    # Verify that the center is within the central room
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[0].x <= cx <= arena.rooms[0].x + arena.rooms[0].width
    assert arena.rooms[0].y <= cy <= arena.rooms[0].y + arena.rooms[0].height

def test_collect_booster_arena_is_point_inside():
    arena = CollectBoosterArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in corner room
    assert arena.is_point_inside(75, 75, 10.0)

    # Point in corridor (horizontal from TL)
    assert arena.is_point_inside(500, 150, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
