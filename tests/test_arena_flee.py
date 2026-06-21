import pytest
from arena.arena_types import FleeArena, get_arena

def test_flee_arena_generation():
    arena = get_arena("flee")
    assert isinstance(arena, FleeArena)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

def test_flee_arena_bounds():
    arena = FleeArena(arena_size=2000.0)
    w, h = arena.width, arena.height
    cx, cy = w/2, h/2

    # Check center is inside
    assert arena.is_point_inside(cx, cy, 10)

    # Check left corner room is inside
    assert arena.is_point_inside(250, cy, 10)

    # Check left corridor is inside
    assert arena.is_point_inside(500, cy, 10)

    # Check an outside point
    assert not arena.is_point_inside(50, 50, 10)

def test_flee_arena_hazards():
    arena = FleeArena()
    hazard = arena.hazards[0]
    assert hazard.kind == "lava"
    assert hazard.radius == 80.0
