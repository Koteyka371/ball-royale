import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import TeamWipesArena

def test_team_wipes_arena_generation():
    arena = TeamWipesArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 2

    # The first room is the central one
    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600

    # The other two are spawn rooms
    for room in arena.rooms[1:]:
        assert room.width == 400
        assert room.height == 400

def test_team_wipes_arena_is_point_inside():
    arena = TeamWipesArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
