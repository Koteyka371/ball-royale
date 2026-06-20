from arena.arena_types import KiteArena, get_arena

def test_kite_arena_generation():
    arena = get_arena("kite", arena_size=1000.0)
    assert isinstance(arena, KiteArena)
    assert len(arena.rooms) == 4

    # Check top room
    assert arena.rooms[0].x == 50
    assert arena.rooms[0].y == 50
    assert arena.rooms[0].width == 1000.0 - 100
    assert arena.rooms[0].height == 200

    # Check bottom room
    assert arena.rooms[1].x == 50
    assert arena.rooms[1].y == 1000.0 - 250
    assert arena.rooms[1].width == 1000.0 - 100
    assert arena.rooms[1].height == 200

    # Check left room
    assert arena.rooms[2].x == 50
    assert arena.rooms[2].y == 250
    assert arena.rooms[2].width == 200
    assert arena.rooms[2].height == 1000.0 - 500

    # Check right room
    assert arena.rooms[3].x == 1000.0 - 250
    assert arena.rooms[3].y == 250
    assert arena.rooms[3].width == 200
    assert arena.rooms[3].height == 1000.0 - 500
