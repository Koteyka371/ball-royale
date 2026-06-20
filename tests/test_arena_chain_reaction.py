import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import get_arena

def test_chain_reaction_arena_generation():
    arena = get_arena('chain_reaction', 2000.0)
    arena.generate()

    # Verify counts
    assert len(arena.rooms) == 4
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 16

    cx, cy = arena.width / 2, arena.height / 2

    # Check that the pillars are non-walkable solid gaps
    # For instance, a pillar exists around center (-325 to -225) on both axes?
    # Corridors:
    # -500 to -325
    # -225 to -50
    # 50 to 225
    # 325 to 500
    # So gaps are at [-325, -225], [-50, 50], [225, 325]

    # The absolute coordinates:
    # For gap around origin: cx - 50 to cx + 50

    # Check a point safely inside the gap
    assert not arena.is_point_inside(cx, cy, 10.0)

    # Check a point inside the corridor
    assert arena.is_point_inside(cx - 150, cy, 10.0)

    # Check a point inside a room
    assert arena.is_point_inside(cx, cy - 600, 10.0)
