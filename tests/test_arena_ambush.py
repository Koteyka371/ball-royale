import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import AmbushArena

def test_ambush_arena_generation():
    arena = AmbushArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    # Main street room
    assert arena.rooms[0].width == 300
    assert arena.rooms[0].height == 600

    # Hiding spots
    for room in arena.rooms[1:]:
        assert room.width == 100
        assert room.height == 100

    # Verify that the center is within the central room
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[0].x <= cx <= arena.rooms[0].x + arena.rooms[0].width
    assert arena.rooms[0].y <= cy <= arena.rooms[0].y + arena.rooms[0].height

def test_ambush_arena_is_point_inside():
    arena = AmbushArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
