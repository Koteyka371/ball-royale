from arena.arena_types import FleeArena

def test_flee_arena_generation():
    arena = FleeArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()
    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 6
    assert len(arena.hazards) == 1
    assert arena.hazards[0].radius == 150.0
