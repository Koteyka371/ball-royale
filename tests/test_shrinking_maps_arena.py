from src.arena.shrinking_maps_arena import ShrinkingMapsArena

def test_shrinking_boundaries():
    arena = ShrinkingMapsArena(1000.0)
    assert arena.min_x == 0.0
    assert arena.max_x == 1000.0

    # Tick 1 with delta 1.0 -> should shrink by 10.0
    arena.update_zone(1, 1.0)
    assert arena.min_x == 10.0
    assert arena.max_x == 990.0

    # Same tick shouldn't shrink again
    arena.update_zone(1, 1.0)
    assert arena.min_x == 10.0
    assert arena.max_x == 990.0

    # Next tick should shrink further
    arena.update_zone(2, 2.0)
    assert arena.min_x == 30.0
    assert arena.max_x == 970.0

def test_clamp_position():
    arena = ShrinkingMapsArena(1000.0)

    # Tick 1 with delta 5.0 -> shrink by 50.0. Bounds: [50.0, 950.0]
    arena.update_zone(1, 5.0)
    assert arena.min_x == 50.0
    assert arena.max_x == 950.0

    # Try clamping a position outside the new bounds. Radius = 10.0
    # Min bounds check: 50.0 + 10.0 = 60.0
    # Max bounds check: 950.0 - 10.0 = 940.0

    # X and Y too low
    x, y, bounced = arena.clamp_position(10.0, 20.0, 10.0)
    assert bounced is True
    # If the point is outside the bounds but not pushed into another procedural bound, it should just be bounded to the shrink map edge.
    # Note: ProceduralArena might also clamp to safe_zone or nearest room. We at least expect it not to be less than 60.0.
    assert x >= 60.0
    assert y >= 60.0

    # X and Y too high
    x, y, bounced = arena.clamp_position(980.0, 990.0, 10.0)
    assert bounced is True
    assert x <= 940.0
    assert y <= 940.0
