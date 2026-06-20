from arena.arena_types import BallGeneticsArena

def test_ball_genetics_arena():
    arena = BallGeneticsArena(arena_size=2000.0, seed=42)

    # Check layout
    assert len(arena.rooms) == 9 # 9 rooms representing base pairs and crossing
    assert len(arena.corridors) == 12 # 4 horizontal connections + 4 left strand + 4 right strand
    assert len(arena.hazards) == 5 # 5 hazards for evolutionary pressure

    # Check if a point in the top-left room is inside
    assert arena.is_point_inside(850, 450, 0)

    # Check if a point in the central crossing room is inside
    assert arena.is_point_inside(1000, 1000, 0)

    # Check if a point far outside is outside
    assert not arena.is_point_inside(5, 5, 0)
