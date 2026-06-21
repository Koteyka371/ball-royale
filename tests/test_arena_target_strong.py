import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import TargetStrongArena

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5

    assert arena.rooms[0].width == 800.0
    assert arena.rooms[0].height == 800.0

    cx, cy = arena.width / 2.0, arena.height / 2.0
    assert arena.hazards[0].x == cx
    assert arena.hazards[0].y == cy
    assert arena.hazards[0].radius == 100.0
    assert arena.hazards[0].kind == "lava"
