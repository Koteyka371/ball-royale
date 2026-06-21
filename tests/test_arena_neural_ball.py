import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import NeuralBallArena

def test_neural_ball_arena_generation():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 4

def test_neural_ball_arena_is_point_inside():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)
    cx, cy = 1000.0, 1000.0

    # Check center room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Check top room
    assert arena.is_point_inside(cx, 100, 10.0)

    # Check out of bounds
    assert not arena.is_point_inside(10, 10, 10.0)
    assert not arena.is_point_inside(1990, 1990, 10.0)
