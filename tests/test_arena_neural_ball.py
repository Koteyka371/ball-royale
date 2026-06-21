import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import NeuralBallArena

def test_neural_ball_arena_generation():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1

    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

    for room in arena.rooms[1:]:
        assert room.width == 300
        assert room.height == 300

def test_neural_ball_arena_is_point_inside():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2
    assert arena.is_point_inside(cx, cy, 10.0)
    assert not arena.is_point_inside(5, 5, 10.0)
