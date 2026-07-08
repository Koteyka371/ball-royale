from arena.arena_types import BallGeneticsArena

def test_ball_genetics_arena():
    arena = BallGeneticsArena(arena_size=2000.0, num_rooms=5, seed=42)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    assert arena.is_point_inside(1000, 1000, 0) # Center
    assert arena.is_point_inside(500, 500, 0) # Top left chamber
    assert not arena.is_point_inside(5, 5, 0) # Outside
