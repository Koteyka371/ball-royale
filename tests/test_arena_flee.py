import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=1000.0, seed=42)

    # Central room + 4 corner rooms = 5 rooms
    assert len(arena.rooms) == 5, f"Expected 5 rooms, got {len(arena.rooms)}"

    # Check corridors count (4 outer + 6 inner)
    assert len(arena.corridors) == 10, f"Expected 10 corridors, got {len(arena.corridors)}"

    # Check bounds
    assert arena.width == 1000.0
    assert arena.height == 1000.0

    # Check that there is at least one hazard
    assert len(arena.hazards) == 1, f"Expected 1 hazard, got {len(arena.hazards)}"
    assert arena.hazards[0].kind == "lava"

def test_flee_arena_point_inside():
    arena = FleeArena(arena_size=1000.0, seed=42)
    # Check center of the first safe corner room (it's from 50 to 250, so 150 is inside)
    assert arena.is_point_inside(150, 150, 10.0)

    # Center room is w/2-300 to w/2+300. For w=1000, cx=500,cy=500. Room is 200 to 800.
    assert arena.is_point_inside(500, 500, 10.0)
