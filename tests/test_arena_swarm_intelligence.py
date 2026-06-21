import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import SwarmIntelligenceArena

def test_swarm_intelligence_arena_generation():
    arena = SwarmIntelligenceArena(arena_size=2000.0, seed=42)

    assert len(arena.rooms) == 9
    assert len(arena.corridors) == 12
    assert len(arena.hazards) == 4

    # Check rooms
    for room in arena.rooms:
        assert room.width == 400
        assert room.height == 400

    # Check hazards
    for hazard in arena.hazards:
        assert hazard.radius == 40.0
        assert hazard.kind == "spikes"
        assert hazard.damage == 25.0

def test_swarm_intelligence_arena_is_point_inside():
    arena = SwarmIntelligenceArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside (negative space hole)
    assert not arena.is_point_inside(5, 5, 10.0)
