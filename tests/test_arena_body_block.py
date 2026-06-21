import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import BodyBlockArena

def test_body_block_arena_generation():
    arena = BodyBlockArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 1
    assert len(arena.hazards) == 2

    # Left base
    assert arena.rooms[0].width == 300
    assert arena.rooms[0].height == 400

def test_body_block_arena_is_point_inside():
    arena = BodyBlockArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in corridor
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in left base
    assert arena.is_point_inside(250, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
