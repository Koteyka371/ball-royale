from arena.arena_types import NeuralBallArena

def test_neural_ball_arena():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

    # Central room
    assert arena.is_point_inside(1000, 1000, 0)

    # Top node
    assert arena.is_point_inside(1000, 650, 0)

    # Outside
    assert not arena.is_point_inside(100, 100, 0)
