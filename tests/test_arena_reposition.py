import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import RepositionArena

def test_reposition_arena_generation():
    arena = RepositionArena(arena_size=2000.0, seed=42)

    # 4 vantage rooms + 1 central room
    assert len(arena.rooms) == 5

    # 4 connecting corridors
    assert len(arena.corridors) == 4

    # Central room hazards
    assert len(arena.hazards) == 12

    # Check bounds
    assert arena.rooms[-1].width == 400
    assert arena.rooms[-1].height == 400

    # Ensure hazads are in the center
    cx, cy = arena.width / 2, arena.height / 2
    for hazard in arena.hazards:
        assert arena.is_point_inside(hazard.x, hazard.y, 0)

def test_reposition_arena_is_point_inside():
    arena = RepositionArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
