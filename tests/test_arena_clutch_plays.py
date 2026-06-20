import pytest
from arena.arena_types import ClutchPlaysArena

def test_clutch_plays_arena_generation():
    arena = ClutchPlaysArena(arena_size=1000.0)

    # Check that rooms are created
    assert len(arena.rooms) == 1
    assert arena.rooms[0].width == 900.0
    assert arena.rooms[0].height == 900.0

    # Check that hazards are generated
    assert len(arena.hazards) > 0

    # Check hazard properties
    for hazard in arena.hazards:
        assert hazard.kind == "lava"
        assert hazard.damage == 80.0

    # Check safe zone logic (no hazards in the very center)
    cx, cy = arena.width / 2, arena.height / 2
    for hazard in arena.hazards:
        import math
        dist_to_center = math.hypot(hazard.x - cx, hazard.y - cy)
        # 150 + 40 (max hazard radius based on grid 10x10 is 100*0.4 = 40)
        assert dist_to_center > 150 - 40, f"Hazard too close to center: {hazard.x}, {hazard.y} (dist: {dist_to_center})"
