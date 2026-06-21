import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import get_arena

def test_ball_genetics_arena_generation():
    arena = get_arena("ball_genetics", arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 0

    # Center room
    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600

    # 4 Nursery rooms
    for i in range(1, 5):
        assert arena.rooms[i].width == 400
        assert arena.rooms[i].height == 400
