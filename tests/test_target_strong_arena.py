import sys
sys.path.insert(0, 'src')

from arena.arena_types import TargetStrongArena, get_arena
from arena.procedural_arena import ProceduralArena

def test_target_strong_arena_registration():
    arena = get_arena("target_strong", arena_size=2000.0)
    assert isinstance(arena, TargetStrongArena)
    assert isinstance(arena, ProceduralArena)

def test_target_strong_arena_generation():
    arena = TargetStrongArena(arena_size=2000.0)
    # The generation is called in __init__, but we can call it again
    arena.generate()

    # We should have the central room, and the corridors
    assert len(arena.rooms) > 0

    # We should have exactly 4 high damage lava hazards in the corners
    assert len(arena.hazards) == 4
    for hazard in arena.hazards:
        assert hazard.kind == "lava"
        assert hazard.damage == 100.0
