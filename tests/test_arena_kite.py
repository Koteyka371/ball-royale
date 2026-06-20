import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import KiteArena

def test_kite_arena_generation():
    arena = KiteArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

    # Verify rooms
    for room in arena.rooms:
        assert room.width == 400
        assert room.height == 400

    # Verify corridors
    for corridor in arena.corridors:
        # width or height should be 200
        assert corridor.width == 200 or corridor.height == 200

def test_kite_arena_is_point_inside():
    arena = KiteArena(arena_size=2000.0, seed=42)
    # Point in top-left room
    assert arena.is_point_inside(200, 200, 10.0)

    # Point in top corridor
    assert arena.is_point_inside(1000, 300, 10.0)

    # Point in central hazard/unwalkable area
    cx, cy = arena.width / 2, arena.height / 2
    # The center itself is unwalkable negative space
    assert not arena.is_point_inside(cx, cy, 10.0)
