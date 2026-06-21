import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import PhysicsChainReactionsArena

def test_physics_chain_reactions_arena_generation():
    arena = PhysicsChainReactionsArena(arena_size=2000.0, seed=42)

    assert len(arena.rooms) == 9
    assert len(arena.corridors) == 12
    assert len(arena.hazards) == 16 # 4 lava + 12 spikes

    # Check rooms
    for room in arena.rooms:
        assert room.width == 400
        assert room.height == 400

    # Check some hazards
    lavas = [h for h in arena.hazards if h.kind == "lava"]
    spikes = [h for h in arena.hazards if h.kind == "spikes"]

    assert len(lavas) == 4
    assert len(spikes) == 12

    for lava in lavas:
        assert lava.damage == 50.0
        assert lava.radius == 50.0

    for s in spikes:
        assert s.damage == 30.0
        assert s.radius == 30.0

def test_physics_chain_reactions_arena_is_point_inside():
    arena = PhysicsChainReactionsArena(arena_size=2000.0, seed=42)

    # Point in central room (offset 800 + 200 = 1000)
    assert arena.is_point_inside(1000, 1000, 10.0)

    # Point outside (in a gap)
    assert not arena.is_point_inside(700, 700, 10.0)
