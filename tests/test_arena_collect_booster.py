import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import CollectBoosterArena

def test_collect_booster_arena_generation():
    arena = CollectBoosterArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 9
    assert len(arena.corridors) == 12
    assert len(arena.hazards) == 1

    # Check that rooms are placed appropriately (just checking width/height here)
    for room in arena.rooms:
        assert room.width == 200
        assert room.height == 200

    # Central hazard
    assert arena.hazards[0].radius == 40.0
    assert arena.hazards[0].kind == "lava"
    assert arena.hazards[0].damage == 25.0

def test_collect_booster_arena_is_point_inside():
    arena = CollectBoosterArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in the top-left room
    assert arena.is_point_inside(cx - 300, cy - 300, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
