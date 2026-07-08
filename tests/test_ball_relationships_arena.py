from arena.arena_types import BallRelationshipsArena

def test_ball_relationships_arena():
    arena = BallRelationshipsArena(arena_size=2000.0, seed=42)

    # Check layout
    assert len(arena.rooms) == 5 # 1 central + 4 spawn rooms
    assert len(arena.corridors) == 8 # 2 per spawn room connecting to center
    assert len(arena.hazards) == 4 # 4 in the center

    # Check if a point in a spawn room is inside
    assert arena.is_point_inside(200, 200, 0)
    # Check if a point in the central room is inside
    assert arena.is_point_inside(1000, 1000, 0)
    # Check if a point outside is outside
    assert not arena.is_point_inside(5, 5, 0)
