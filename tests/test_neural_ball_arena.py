from arena.arena_types import NeuralBallArena

def test_neural_ball_arena():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1

    # Check center
    assert arena.is_point_inside(1000, 1000, 0)

    # Check hazards
    assert arena.hazards[0].kind == "lava"
    assert arena.hazards[0].damage == 20.0
