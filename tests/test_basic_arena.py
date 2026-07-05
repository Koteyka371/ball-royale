import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.basic_arena import BasicArena

def test_get_random_spawn_point():
    arena = BasicArena(arena_size=1000.0, seed=42)
    radius = 10.0
    for _ in range(100):
        x, y = arena.get_random_spawn_point(radius)
        assert arena.is_point_inside(x, y, radius)

def test_is_point_inside():
    arena = BasicArena(arena_size=1000.0)
    radius = 10.0

    assert arena.is_point_inside(500, 500, radius)
    assert not arena.is_point_inside(5, 500, radius)
    assert not arena.is_point_inside(500, 5, radius)
    assert not arena.is_point_inside(995, 500, radius)
    assert not arena.is_point_inside(500, 995, radius)

def test_clamp_position():
    arena = BasicArena(arena_size=1000.0)
    radius = 10.0

    # Inside point
    x, y, bounced = arena.clamp_position(500, 500, radius)
    assert x == 500
    assert y == 500
    assert not bounced

    # Outside left
    x, y, bounced = arena.clamp_position(5, 500, radius)
    assert x == 10
    assert y == 500
    assert bounced

    # Outside top
    x, y, bounced = arena.clamp_position(500, 5, radius)
    assert x == 500
    assert y == 10
    assert bounced

    # Outside right
    x, y, bounced = arena.clamp_position(995, 500, radius)
    assert x == 990
    assert y == 500
    assert bounced

    # Outside bottom
    x, y, bounced = arena.clamp_position(500, 995, radius)
    assert x == 500
    assert y == 990
    assert bounced

    # Diagonal outside
    x, y, bounced = arena.clamp_position(5, 5, radius)
    # The shrink zone is applied so x/y are modified beyond standard bounds.
    assert bounced

def test_update_zone():
    arena = BasicArena(arena_size=1000.0)
    assert arena.safe_zone_radius == 700.0

    arena.update_zone(0, 1.0)
    assert arena.safe_zone_radius == 690.0

    # Same tick shouldn't update
    arena.update_zone(0, 1.0)
    assert arena.safe_zone_radius == 690.0

    # Clamp to min size
    arena.update_zone(1, 100.0)
    assert arena.safe_zone_radius == 0.0
