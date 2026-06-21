import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1

    # Central hazard
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.hazards[0].x == cx
    assert arena.hazards[0].y == cy
    assert arena.hazards[0].radius == 50.0
    assert arena.hazards[0].kind == "lava"

def test_flee_arena_is_point_inside():
    arena = FleeArena(arena_size=2000.0, seed=42)

    # Point in top-left room
    assert arena.is_point_inside(100.0, 100.0, 10.0)

    # Point outside bounds
    assert not arena.is_point_inside(5.0, 5.0, 10.0)
