import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import MetaEvolutionArena

def test_meta_evolution_arena_generation():
    arena = MetaEvolutionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 4

    # Verify rooms
    for room in arena.rooms:
        assert room.width in [200, 300]
        assert room.height in [200, 300]

    # Verify corridors
    for corridor in arena.corridors:
        # width or height should be 100
        assert corridor.width == 100 or corridor.height == 100

def test_meta_evolution_arena_is_point_inside():
    arena = MetaEvolutionArena(arena_size=2000.0, seed=42)

    # Point in top-left room
    assert arena.is_point_inside(150, 150, 10.0)

    # Point in central room
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in an unwalkable area (between outer and inner rooms, outside of corridor)
    assert not arena.is_point_inside(cx - 200, cy - 200, 10.0)
