import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import HealAllyArena

def test_heal_ally_arena_generation():
    arena = HealAllyArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 1

def test_heal_ally_arena_is_point_inside():
    arena = HealAllyArena(arena_size=2000.0, seed=42)
    w, h = arena.width, arena.height
    cx, cy = w/2, h/2

    # Point inside the central room
    assert arena.is_point_inside(cx, cy - 100, 10.0)

    # Point outside
    assert not arena.is_point_inside(10.0, 10.0, 10.0)
