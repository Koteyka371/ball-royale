import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0, seed=42)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

    assert arena.rooms[0].width == 800
    assert arena.hazards[0].radius == 80.0

def test_target_strong_arena_is_point_inside():
    arena = TargetStrongArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)
