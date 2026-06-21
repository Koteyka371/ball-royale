import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

    # Central room
    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

    # Outer rooms
    assert arena.rooms[1].width == 200
    assert arena.rooms[1].height == 200

    # Corridors
    assert arena.corridors[0].width == 100
    assert arena.corridors[0].height == 650

    # Hazards
    assert arena.hazards[0].radius == 30.0
    assert arena.hazards[0].kind == "lava"

def test_flee_arena_is_point_inside():
    arena = FleeArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
