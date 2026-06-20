import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import BodyBlockArena

def test_body_block_arena_generation():
    arena = BodyBlockArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 0
    assert len(arena.hazards) == 0

    # The first two rooms are the large ones
    assert arena.rooms[0].width == 1900
    assert arena.rooms[1].width == 1900

    # The other three are narrow corridors
    for room in arena.rooms[2:]:
        assert room.width == 100

def test_body_block_arena_is_point_inside():
    arena = BodyBlockArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in one of the central corridors
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside (in the void between corridors)
    assert not arena.is_point_inside(cx - 150, cy, 10.0)
