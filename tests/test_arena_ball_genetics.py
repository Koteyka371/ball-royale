import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import BallGeneticsArena

def test_ball_genetics_arena_generation():
    arena = BallGeneticsArena(arena_size=2000.0)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5

    # Check that all rooms are inside arena bounds
    for room in arena.rooms:
        assert room.x >= 0 and room.y >= 0
        assert room.x + room.width <= arena.width
        assert room.y + room.height <= arena.height
