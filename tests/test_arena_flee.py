import pytest
from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=1000.0, num_rooms=5, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 0

    # Test center room bounding box based on logic: w,h = 1000, cx,cy = 500
    center_room = arena.rooms[0]
    assert center_room.x == 350 # 500 - 150
    assert center_room.y == 350
    assert center_room.width == 300
    assert center_room.height == 300

    # Ensure a point in the center room is inside
    assert arena.is_point_inside(500, 500, 10)
