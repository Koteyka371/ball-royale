import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import AmbushArena

def test_ambush_arena_generation():
    arena = AmbushArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1

    # Central room
    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600

    # Hiding spots
    for room in arena.rooms[1:]:
        assert room.width == 150
        assert room.height == 150

    # Verify that the hazard is in the center
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.hazards[0].x == cx
    assert arena.hazards[0].y == cy
    assert arena.hazards[0].radius == 80.0
    assert arena.hazards[0].kind == "lava"

def test_ambush_arena_is_point_inside():
    arena = AmbushArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in top-left hiding spot
    assert arena.is_point_inside(100.0, 100.0, 10.0)

    # Point outside bounds
    assert not arena.is_point_inside(5.0, 5.0, 10.0)
