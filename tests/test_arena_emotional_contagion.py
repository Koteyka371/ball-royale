import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena_generation():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

    # Central room
    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

    # Test all side rooms are correctly generated
    for room in arena.rooms[1:]:
        assert room.width == 200
        assert room.height == 200

def test_emotional_contagion_arena_is_point_inside():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in top room
    assert arena.is_point_inside(cx, 100, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
