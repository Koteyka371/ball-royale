from arena.arena_types import NeuralBallArena

def test_neural_ball_arena():
    arena = NeuralBallArena(arena_size=1000.0, num_rooms=3, seed=42)
    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 1
    assert len(arena.hazards) == 2
