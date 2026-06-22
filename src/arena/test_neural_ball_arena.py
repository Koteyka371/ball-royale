import pytest
from arena.arena_types import NeuralBallArena

def test_neural_ball_arena_generation():
    arena = NeuralBallArena(arena_size=2000.0, num_rooms=5, seed=42)
    arena.generate()

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 2

    # Check center room dimensions
    center_room = arena.rooms[0]
    assert center_room.width == 600.0
    assert center_room.height == 600.0

    # Check a hazard
    assert arena.hazards[0].kind == "lava"
    assert arena.hazards[0].radius == 30.0
