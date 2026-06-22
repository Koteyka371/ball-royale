from arena.arena_types import BodyBlockArena

def test_body_block_arena_generation():
    arena = BodyBlockArena(arena_size=2000.0)

    # 3 rooms (central, left base, right base)
    assert len(arena.rooms) == 3

    # 2 corridors
    assert len(arena.corridors) == 2

    # 1 hazard
    assert len(arena.hazards) == 1
    assert arena.hazards[0].kind == "lava"
    assert arena.hazards[0].radius == 50.0
