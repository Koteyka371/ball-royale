import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import CircleStrafeArena

def test_circle_strafe_arena_generation():
    arena = CircleStrafeArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 1
    assert len(arena.corridors) == 0
    assert len(arena.hazards) == 1

    room = arena.rooms[0]
    assert room.width == 1800
    assert room.height == 1800

    # Check that hazard is placed correctly in the center
    cx, cy = arena.width / 2, arena.height / 2
    hazard = arena.hazards[0]
    assert hazard.x == cx
    assert hazard.y == cy
    assert hazard.radius == 300.0
    assert hazard.kind == "lava"
    assert hazard.damage == 50.0

def test_circle_strafe_arena_is_point_inside():
    arena = CircleStrafeArena(arena_size=2000.0, seed=42)

    # Point in central room but avoiding the hazard
    # The room is from 100 to 1900. Center is 1000, 1000.
    assert arena.is_point_inside(200, 200, 10.0)

    # Point outside the room entirely
    assert not arena.is_point_inside(50, 50, 10.0)
