import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import BodyBlockArena

def test_body_block_arena_generation():
    arena = BodyBlockArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 6
    assert len(arena.hazards) == 2

    # Check rooms
    left_base = arena.rooms[0]
    right_base = arena.rooms[1]
    center_room = arena.rooms[2]

    assert left_base.width == 300
    assert left_base.height == 600
    assert right_base.width == 300
    assert right_base.height == 600
    assert center_room.width == 600
    assert center_room.height == 800

    # Check hazards
    for h in arena.hazards:
        assert h.kind == "lava"
        assert h.damage == 20.0
        assert h.radius == 50.0

def test_body_block_arena_is_point_inside():
    arena = BodyBlockArena(arena_size=2000.0, seed=42)
    w, h = arena.width, arena.height
    cx, cy = w/2, h/2

    # In center room
    assert arena.is_point_inside(cx, cy, 10.0)

    # In left base
    assert arena.is_point_inside(100, cy, 10.0)

    # In right base
    assert arena.is_point_inside(w - 100, cy, 10.0)

    # In left corridor 1
    assert arena.is_point_inside(500, cy - 160, 10.0)

    # Out of bounds
    assert not arena.is_point_inside(5, 5, 10.0)
