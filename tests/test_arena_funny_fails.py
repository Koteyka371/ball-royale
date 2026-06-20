import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import FunnyFailsArena

def test_funny_fails_arena_generation():
    arena = FunnyFailsArena(arena_size=2000.0)

    # Check 1 large room
    assert len(arena.rooms) == 1

    # Room size should take almost the whole arena
    room = arena.rooms[0]
    assert room.x == 50
    assert room.y == 50
    assert room.width == 1900
    assert room.height == 1900

    # 5x5 grid minus the center = 24 hazards
    assert len(arena.hazards) == 24

    # Check hazards logic
    has_spikes = False
    has_lava = False
    for hazard in arena.hazards:
        # Expected radius calculation: min(380, 380)/2 - 30 = 160
        assert hazard.radius == 160.0
        if hazard.kind == "spikes":
            has_spikes = True
            assert hazard.damage == 20.0
        elif hazard.kind == "lava":
            has_lava = True
            assert hazard.damage == 40.0

    assert has_spikes
    assert has_lava

def test_funny_fails_center_safe_zone():
    arena = FunnyFailsArena(arena_size=2000.0)

    # Verify no hazard in the direct center
    # Center cell is i=2, j=2.
    # cell_w = 380, cell_h = 380
    # hx = 50 + 2*380 + 190 = 1000
    # hy = 50 + 2*380 + 190 = 1000

    for hazard in arena.hazards:
        assert not (hazard.x == 1000.0 and hazard.y == 1000.0)
