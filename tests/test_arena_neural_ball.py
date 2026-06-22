import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import NeuralBallArena

def test_neural_ball_arena_generation():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4
    assert arena.width == 2000.0
    assert arena.height == 2000.0
