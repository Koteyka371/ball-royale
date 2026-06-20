import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import NeuralArena

def test_neural_arena_generation():
    arena = NeuralArena(arena_size=2000.0, seed=42)

    # 3 layers with 3, 4, 2 nodes
    assert len(arena.rooms) == 9

    # 2 buses + connections
    # 1st layer (3) to bus1 + 2nd layer (4) to bus1/bus2 + 3rd layer (2) to bus2 = 3 + 8 + 2 = 13 + 2 buses = 15 corridors
    assert len(arena.corridors) == 15

    # First layer should be on the left
    assert arena.rooms[0].x < arena.rooms[3].x

def test_neural_arena_is_point_inside():
    arena = NeuralArena(arena_size=2000.0, seed=42)

    # Let's test the center of the first node
    w, h = arena.width, arena.height
    cx = w * 0.15
    cy = h * 0.2

    # Should be inside
    assert arena.is_point_inside(cx, cy, 10.0)

    # Way outside
    assert not arena.is_point_inside(10, 10, 10.0)
