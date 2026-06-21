import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena_generation():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 4

    # Central room
    assert arena.rooms[4].width == 400
    assert arena.rooms[4].height == 400

    # Verify that the center is within the central room
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[4].x <= cx <= arena.rooms[4].x + arena.rooms[4].width
    assert arena.rooms[4].y <= cy <= arena.rooms[4].y + arena.rooms[4].height

def test_emotional_contagion_arena_is_point_inside():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
