import pytest
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    # Check dimensions
    cx = 1000.0
    cy = 1000.0

    # Check center hazard
    haz0 = arena.hazards[0]
    assert haz0.x == cx
    assert haz0.y == cy
    assert haz0.radius == 100.0
    assert haz0.kind == "lava"

    # Check inside boundary for a point inside the central room
    # The central room is cx - 300 to cx + 300 (700 to 1300)
    assert arena.is_point_inside(cx, cy, 10.0) == True

def test_target_strong_arena_point_outside():
    arena = TargetStrongArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()

    # Check outside boundary (e.g., origin point which should be outside all rooms)
    # The rooms are:
    # 100 to 300 (x and y)
    # w-300 to w-100 (1700 to 1900)
    # ...
    # So (10, 10) is outside
    assert arena.is_point_inside(10.0, 10.0, 5.0) == False
