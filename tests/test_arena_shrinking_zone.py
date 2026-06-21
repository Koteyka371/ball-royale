import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import get_arena

def test_shrinking_zone_arena_generation():
    arena = get_arena("shrinking_zone", arena_size=2000.0)
    assert len(arena.rooms) == 1
    assert len(arena.corridors) == 0
    assert len(arena.hazards) == 8

    room = arena.rooms[0]
    assert room.x == 100.0
    assert room.y == 100.0
    assert room.width == 1800.0
    assert room.height == 1800.0

def test_shrinking_zone_arena_update_zone():
    arena = get_arena("shrinking_zone", arena_size=1000.0)
    assert arena.safe_zone_radius == 700.0

    # Test faster shrink rate
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 670.0 # 700 - 30

    # Same tick should not shrink again
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 670.0

    # Next tick shrinks again
    arena.update_zone(2, 2.0)
    assert arena.safe_zone_radius == 610.0 # 670 - 60

def test_shrinking_zone_arena_minimum_radius():
    arena = get_arena("shrinking_zone", arena_size=100.0)
    assert arena.safe_zone_radius == 70.0

    # Massive delta to hit minimum
    arena.update_zone(1, 10.0)
    assert arena.safe_zone_radius == 20.0 # Minimum is 20 for this arena, not 50

    arena.update_zone(2, 10.0)
    assert arena.safe_zone_radius == 20.0
