import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import HideBehindArena


def test_hide_behind_arena_generation():
    arena = HideBehindArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 6
    assert len(arena.corridors) == 0
    assert len(arena.hazards) == 0

    # 3 vertical strip rooms + 3 horizontal strip rooms
    w, h = arena.width, arena.height

    # Verify bounds of generated geometry to ensure points within the bounds
    # but not inside the "pillars" are valid spawn points.

    # Middle of an intersection should be valid
    assert arena.is_point_inside(50 + 200/2, 50 + 200/2, 10)

    # The gaps are pillars. We have 3 vertical strips and 3 horizontal strips.
    # The first vertical strip is at x=50, width=200.
    # The first gap is at x=250.
    # The first horizontal strip is at y=50, height=200.
    # The first gap is at y=250.
    # So the point (250 + gap_x/2, 250 + gap_y/2) is in a pillar and should NOT be inside any room.

    strip_w = 200
    gap_x = (w - 100 - 3 * strip_w) / 2
    gap_y = (h - 100 - 3 * strip_w) / 2

    # Verify that a pillar point is not inside
    pillar_x = 50 + strip_w + gap_x / 2
    pillar_y = 50 + strip_w + gap_y / 2
    assert not arena.is_point_inside(pillar_x, pillar_y, 0)

    # Outside arena
    assert not arena.is_point_inside(5, 5, 10)
