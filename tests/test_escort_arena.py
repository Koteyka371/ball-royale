from arena.arena_types import EscortArena

def test_escort_arena_generation():
    arena = EscortArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()
    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 1
    assert len(arena.hazards) == 2
