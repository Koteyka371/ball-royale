import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TargetWeakArena

def test_target_weak_arena_generation():
    arena = TargetWeakArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4

    # Central room
    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600

    # Hiding rooms
    for room in arena.rooms[1:]:
        assert room.width == 150
        assert room.height == 150

    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[0].x <= cx <= arena.rooms[0].x + arena.rooms[0].width
    assert arena.rooms[0].y <= cy <= arena.rooms[0].y + arena.rooms[0].height

def test_target_weak_arena_is_point_inside():
    arena = TargetWeakArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Center is inside
    assert arena.is_point_inside(cx, cy, 10.0)

    # Edge corner is inside hiding room
    assert arena.is_point_inside(100, 100, 5.0)

    # Top center is outside
    assert not arena.is_point_inside(cx, 10, 5.0)
