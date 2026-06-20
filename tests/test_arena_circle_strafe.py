import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import CircleStrafeArena

def test_circle_strafe_arena_generation():
    arena = CircleStrafeArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 1
    assert len(arena.hazards) == 1

    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[0].width == 1200
    assert arena.rooms[0].height == 1200
    assert arena.rooms[0].x == cx - 600
    assert arena.rooms[0].y == cy - 600

    assert arena.hazards[0].x == cx
    assert arena.hazards[0].y == cy
    assert arena.hazards[0].radius == 300.0
    assert arena.hazards[0].kind == "lava"

def test_circle_strafe_arena_is_point_inside():
    arena = CircleStrafeArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point near the hazard but still inside the room
    assert arena.is_point_inside(cx + 400, cy, 10.0)

    # Point clearly outside the room
    assert not arena.is_point_inside(5, 5, 10.0)
