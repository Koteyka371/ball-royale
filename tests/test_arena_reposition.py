from arena.arena_types import RepositionArena

def test_reposition_arena_generation():
    arena = RepositionArena(arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1
    for room in arena.rooms:
        assert room.width > 0 and room.height > 0
    for corridor in arena.corridors:
        assert corridor.width > 0 and corridor.height > 0
