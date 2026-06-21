from arena.arena_types import NeuralBallArena

def test_neural_ball_arena_generation():
    arena = NeuralBallArena(arena_size=2000.0)

    # 4 input, 3 hidden, 2 output rooms = 9 rooms total
    assert len(arena.rooms) == 9

    # 4 corridors from input to hidden, 3 from hidden to output = 7 corridors total
    assert len(arena.corridors) == 7

    # 1 hazard
    assert len(arena.hazards) == 1

    # Verify input room pos
    assert arena.rooms[0].width == 100
