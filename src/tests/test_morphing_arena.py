import pytest
from arena.morphing_arena import MorphingArena
import math

def test_morphing_arena():
    arena = MorphingArena()
    arena.generate()

    assert arena.name == "morphing"
    assert len(arena.rooms) == 0
    assert len(arena.corridors) == 0

    arena.update_zone(0, 1.0)

    # Box phase
    cx, cy = arena.width / 2.0, arena.height / 2.0
    assert arena.is_point_inside(cx, cy, 10.0)

    # Move to phase
    arena.update_zone(1200, 1.0)

    # Check clamps
    nx, ny, bounced = arena.clamp_position(-1000, -1000, 10.0)
    assert bounced
    assert arena.is_point_inside(nx, ny, 10.0)

    # Move to phase 2
    arena.update_zone(2400, 1.0)
    nx, ny, bounced = arena.clamp_position(-1000, -1000, 10.0)
    assert bounced
    assert arena.is_point_inside(nx, ny, 10.0)
