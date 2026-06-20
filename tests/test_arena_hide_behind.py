import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import HideBehindArena

def test_hide_behind_arena_generation():
    arena = HideBehindArena(arena_size=2000.0, seed=42)
    # The generation creates a large central room, then clears it and adds a grid of rooms (corridors acting as rooms)
    # We should have more than 0 rooms and corridors (actually we clear corridors and use rooms for everything)
    assert len(arena.rooms) > 0
    assert len(arena.corridors) == 0

    # We should find that some points are valid and others (pillars) are not.
    # Central room was added, then cleared, then grid was added.
    # grid has gap = 150, pillar = 200.

    # Pillar top-left should be roughly x=50+150=200, y=200. Width=200, height=200.
    # So (300, 300) should be inside a pillar, and thus NOT inside any room.
    assert not arena.is_point_inside(300, 300, 10.0)

def test_hide_behind_arena_is_point_inside():
    arena = HideBehindArena(arena_size=2000.0, seed=42)

    # A point on the grid lines (x=100, y=100) should be inside a room.
    assert arena.is_point_inside(100, 100, 10.0)

    # A point far outside the arena shouldn't be inside.
    assert not arena.is_point_inside(5, 5, 10.0)
