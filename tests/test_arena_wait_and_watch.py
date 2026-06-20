import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import WaitAndWatchArena

def test_wait_and_watch_arena_generation():
    arena = WaitAndWatchArena(arena_size=2000.0)
    arena.generate()

    # 1 central room + 4 corner rooms
    assert len(arena.rooms) == 5

    # 2 corridor segments per corner = 8 corridors
    assert len(arena.corridors) == 8

    # 12 inner circle + 8 outer circle + 1 center = 21 hazards
    assert len(arena.hazards) == 21

    # Check connection
    central_room = arena.rooms[0]

    # Check bounding box size of central room
    assert central_room.width == 600
    assert central_room.height == 600
