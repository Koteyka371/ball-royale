import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import PhysicsChainReactionsArena

def test_physics_chain_reactions_arena_generation():
    arena = PhysicsChainReactionsArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5

    # Central room
    assert arena.rooms[0].width == 600
    assert arena.rooms[0].height == 600

    cx, cy = arena.width / 2, arena.height / 2
    assert arena.hazards[4].x == cx
    assert arena.hazards[4].y == cy
    assert arena.hazards[4].radius == 80.0
    assert arena.hazards[4].kind == "lava"

def test_physics_chain_reactions_arena_is_point_inside():
    arena = PhysicsChainReactionsArena(arena_size=2000.0, seed=42)
    cx, cy = arena.width / 2, arena.height / 2

    # Point in central room
    assert arena.is_point_inside(cx, cy, 10.0)

    # Point outside bounds
    assert not arena.is_point_inside(5.0, 5.0, 10.0)
