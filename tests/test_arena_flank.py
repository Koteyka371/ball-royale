import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FlankArena, get_arena

def test_flank_arena_generation():
    arena = FlankArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4

    # The first room is the central one
    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

    # The other four are flanking rooms
    for room in arena.rooms[1:]:
        assert room.width in [150, 200]
        assert room.height in [150, 200]

    # Verify that the center is within the central room
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[0].x <= cx <= arena.rooms[0].x + arena.rooms[0].width
    assert arena.rooms[0].y <= cy <= arena.rooms[0].y + arena.rooms[0].height

def test_flank_arena_is_point_inside():
    arena = FlankArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)

def test_circle_strafe_arena():
    arena = get_arena("circle_strafe", arena_size=1000.0)
    assert len(arena.rooms) == 1
    assert len(arena.hazards) == 5
