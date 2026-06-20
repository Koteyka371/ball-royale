import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import WaitAndWatchArena

def test_wait_and_watch_arena_generation():
    arena = WaitAndWatchArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 12

    # Central room
    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600

    # Test top and bottom outer ring rooms
    assert arena.rooms[1].width == 1900  # 2000 - 2*50
    assert arena.rooms[1].height == 150
    assert arena.rooms[2].width == 1900
    assert arena.rooms[2].height == 150

    # Test left and right outer ring rooms
    assert arena.rooms[3].width == 150
    assert arena.rooms[3].height == 1600 # 2000 - 2*50 - 2*150
    assert arena.rooms[4].width == 150
    assert arena.rooms[4].height == 1600

def test_wait_and_watch_arena_is_point_inside():
    arena = WaitAndWatchArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point in outer ring (top room)
    assert arena.is_point_inside(cx, 100, 10.0)

    # Point outside bounds
    assert not arena.is_point_inside(10, 10, 10.0)
