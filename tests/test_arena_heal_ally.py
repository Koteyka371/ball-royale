import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import HealAllyArena

def test_heal_ally_arena_generation():
    arena = HealAllyArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 0

    # Center room
    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600

    # Safe rooms
    assert arena.rooms[1].width == 200
    assert arena.rooms[1].height == 200
    assert arena.rooms[2].width == 200
    assert arena.rooms[2].height == 200

def test_heal_ally_arena_is_point_inside():
    arena = HealAllyArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in left safe room
    assert arena.is_point_inside(100, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(10, 10, 10.0)
