import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import UseShieldArena

def test_use_shield_arena_generation():
    arena = UseShieldArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 1
    assert len(arena.corridors) == 0
    assert len(arena.hazards) == 24

    room = arena.rooms[0]
    assert room.width == 800
    assert room.height == 800

    # Check that hazards are placed correctly
    cx, cy = arena.width / 2, arena.height / 2
    for hazard in arena.hazards:
        dist = math.hypot(hazard.x - cx, hazard.y - cy)
        # It should be placed at a radius of 250 from center
        assert abs(dist - 250) < 1.0
        assert hazard.radius == 40.0
        assert hazard.kind in ["spikes", "lava"]
        assert hazard.damage in [20.0, 40.0]

def test_use_shield_arena_is_point_inside():
    arena = UseShieldArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside
    assert not arena.is_point_inside(5, 5, 10.0)
