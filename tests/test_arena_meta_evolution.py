import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from arena.arena_types import MetaEvolutionArena

def test_meta_evolution_arena_generation():
    arena = MetaEvolutionArena(arena_size=2000.0)

    # Should have exactly 4 rooms: 1 center + 3 branches
    assert len(arena.rooms) == 4

    # Should have exactly 3 corridors connecting the branches
    assert len(arena.corridors) == 3

    # Should have 5 hazards
    assert len(arena.hazards) == 5

    # Check that all rooms are inside arena bounds
    for room in arena.rooms:
        assert room.x >= 0 and room.y >= 0
        assert room.x + room.width <= arena.width
        assert room.y + room.height <= arena.height
