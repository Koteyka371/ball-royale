import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EpicKillsArena

def test_epic_kills_arena_generation():
    arena = EpicKillsArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 8

def test_epic_kills_arena_is_point_inside():
    arena = EpicKillsArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point inside the central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point inside the left nest
    assert arena.is_point_inside(cx - 600, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(10, 10, 10.0)
