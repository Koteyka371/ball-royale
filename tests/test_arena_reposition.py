import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import RepositionArena

def test_reposition_arena_generation():
    arena = RepositionArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 9
    assert len(arena.corridors) == 12
    assert len(arena.hazards) == 12

    for room in arena.rooms:
        assert room.width == 200
        assert room.height == 200

def test_reposition_arena_is_point_inside():
    arena = RepositionArena(arena_size=2000.0, seed=42)

    # Point in first island (200, 200) to (400, 400)
    # Using 10.0 radius so bounds are 210 to 390
    assert arena.is_point_inside(300, 300, 10.0)

    # Point outside (in the gap between islands)
    # e.g. x=500, y=300
    assert not arena.is_point_inside(500, 500, 10.0)

    # Point inside the horizontal corridor connecting (200, 200) and (900, 200)
    # The corridor starts at rx1+150 = 350, y=260, w=600, h=80
    assert arena.is_point_inside(600, 300, 10.0)
