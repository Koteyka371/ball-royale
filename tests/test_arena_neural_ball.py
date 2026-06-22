import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import NeuralBallArena

def test_arena_neural_ball():
    arena = NeuralBallArena(arena_size=2000.0)
    w = 2000.0
    h = 2000.0

    assert len(arena.rooms) == 8
    assert len(arena.corridors) == 7
    assert len(arena.hazards) == 2

    assert arena.is_point_inside(w * 0.1 + 75.0, h * 0.2 + 75.0, 10.0)
