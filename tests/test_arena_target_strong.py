import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1

    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600
    for room in arena.rooms[1:]:
        assert room.width == 200
        assert room.height == 200

    cx, cy = arena.width / 2, arena.height / 2
    assert arena.hazards[0].x == cx
    assert arena.hazards[0].y == cy
    assert arena.hazards[0].radius == 120.0
    assert arena.hazards[0].kind == "lava"

def test_target_strong_arena_is_point_inside():
    arena = TargetStrongArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    assert arena.is_point_inside(cx, cy, 10.0)
    assert arena.is_point_inside(150.0, 150.0, 10.0)
    assert not arena.is_point_inside(5.0, 5.0, 10.0)
