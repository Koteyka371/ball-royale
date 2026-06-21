import pytest
from arena.arena_types import AmbushArena

def test_ambush_arena_generation():
    arena = AmbushArena(arena_size=2000.0)
    arena.generate()

    # Ambush arena should have exactly 5 rooms:
    # 1 central room, 4 ambush hiding spots (dead ends)
    assert len(arena.rooms) == 5

    # Should have 4 corridors connecting the dead ends to the center
    assert len(arena.corridors) == 4

    # The four dead end rooms should be smaller than the central one
    central_room = arena.rooms[0]
    for i in range(1, 5):
        assert arena.rooms[i].width < central_room.width
        assert arena.rooms[i].height < central_room.height
