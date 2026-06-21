import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import NeuralBallArena

def test_neural_ball_arena_generation():
    arena = NeuralBallArena(arena_size=2000.0, seed=42)

    assert len(arena.rooms) == 9
    assert len(arena.corridors) == 10
    assert len(arena.hazards) == 3

    for room in arena.rooms:
        assert room.width == 200.0
        assert room.height == 200.0

    for hazard in arena.hazards:
        assert hazard.radius == 40.0
        assert hazard.kind == "lava"
        assert hazard.damage == 30.0
