import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import GroupAttackArena

def test_group_attack_arena_generation():
    arena = GroupAttackArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 4

    # The first room is the central one
    assert arena.rooms[0].width == 800
    assert arena.rooms[0].height == 800

    # The other four are staging rooms
    for room in arena.rooms[1:]:
        assert room.width == 300
        assert room.height == 300

    # Verify that the center is within the central room
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[0].x <= cx <= arena.rooms[0].x + arena.rooms[0].width
    assert arena.rooms[0].y <= cy <= arena.rooms[0].y + arena.rooms[0].height

    # Verify hazards
    for h in arena.hazards:
        assert h.kind == "lava"
        assert h.radius == 50

def test_group_attack_arena_is_point_inside():
    arena = GroupAttackArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in staging rooms
    assert arena.is_point_inside(100, 100, 10.0) # Top-Left
    assert arena.is_point_inside(1900, 100, 10.0) # Top-Right
    assert arena.is_point_inside(100, 1900, 10.0) # Bottom-Left
    assert arena.is_point_inside(1900, 1900, 10.0) # Bottom-Right

    # Point outside (in gaps between rooms and corridors)
    assert not arena.is_point_inside(5, 5, 10.0)
    assert not arena.is_point_inside(cx, 100, 10.0)
