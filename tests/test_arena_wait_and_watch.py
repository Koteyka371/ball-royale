import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import WaitAndWatchArena

def test_wait_and_watch_arena_generation():
    arena = WaitAndWatchArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600
    assert arena.rooms[1].width == 200
    assert arena.rooms[1].height == 200

    cx, cy = arena.width / 2, arena.height / 2
    assert arena.hazards[0].x == cx
    assert arena.hazards[0].y == cy
    assert arena.hazards[0].radius == 100.0
    assert arena.hazards[0].kind == "lava"

def test_wait_and_watch_arena_is_point_inside():
    arena = WaitAndWatchArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # In center room
    assert arena.is_point_inside(cx, cy, 10.0)

    # In a corner room
    assert arena.is_point_inside(150.0, 150.0, 10.0)

    # Outside
    assert not arena.is_point_inside(5.0, 5.0, 10.0)
