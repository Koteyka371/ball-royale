import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena_generation():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 4

    cx, cy = arena.width / 2, arena.height / 2
    assert arena.rooms[0].width == 800
    assert arena.rooms[0].height == 800

    assert arena.hazards[0].x == cx - 250
    assert arena.hazards[0].y == cy - 250
    assert arena.hazards[0].radius == 30.0

def test_emotional_contagion_arena_is_point_inside():
    arena = EmotionalContagionArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    assert arena.is_point_inside(cx, cy, 10.0)
    assert arena.is_point_inside(150.0, 150.0, 10.0)
    assert not arena.is_point_inside(5.0, 5.0, 10.0)
