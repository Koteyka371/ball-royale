import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import BallGeneticsArena

def test_ball_genetics_arena_generation():
    arena = BallGeneticsArena(arena_size=2000.0)

    # 1 center testing ground + 4 breeding pens
    assert len(arena.rooms) == 5

    # 4 horizontal + 4 vertical corridors connecting pens to center
    assert len(arena.corridors) == 8

    # 1 central lava + 4 poison mutations
    assert len(arena.hazards) == 5

    # Bounds validation
    for room in arena.rooms:
        assert room.x >= 0 and room.y >= 0
        assert room.x + room.width <= arena.width
        assert room.y + room.height <= arena.height

    for corridor in arena.corridors:
        assert corridor.x >= 0 and corridor.y >= 0
        assert corridor.x + corridor.width <= arena.width
        assert corridor.y + corridor.height <= arena.height

    for hz in arena.hazards:
        assert hz.x - hz.radius >= 0 and hz.x + hz.radius <= arena.width
        assert hz.y - hz.radius >= 0 and hz.y + hz.radius <= arena.height
