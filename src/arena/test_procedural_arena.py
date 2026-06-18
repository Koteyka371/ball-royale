import pytest
from arena.procedural_arena import ProceduralArena

def test_arena_generation():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) > 0

def test_random_spawn():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    x, y = arena.get_random_spawn_point(10.0)
    assert arena.is_point_inside(x, y, 10.0)

def test_clamp_position():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    # Get a point inside
    rx, ry = arena.rooms[0].x + 50, arena.rooms[0].y + 50
    cx, cy, bounced = arena.clamp_position(rx, ry, 10.0)
    assert not bounced
    assert cx == rx and cy == ry

    # Get a point outside
    ox, oy = -100, -100
    cx, cy, bounced = arena.clamp_position(ox, oy, 10.0)
    assert bounced
    assert arena.is_point_inside(cx, cy, 10.0)
