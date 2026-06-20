from arena.arena_types import ChainReactionArena

def test_arena_generation():
    arena = ChainReactionArena(arena_size=2000.0)
    arena.generate()

    assert len(arena.rooms) == 10
    assert len(arena.hazards) == 12
    for hazard in arena.hazards:
        assert hazard.kind == "spikes"
