from arena.procedural_arena import ProceduralArena

def test_zone_shrinks():
    arena = ProceduralArena(arena_size=1000.0)
    assert arena.safe_zone_radius == 700.0
    assert arena.safe_zone_center == (500.0, 500.0)

    # Tick 1
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 690.0

    # Same tick shouldn't shrink again
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 690.0

    # Next tick should shrink
    arena.update_zone(2, 2.0)
    assert arena.safe_zone_radius == 670.0

def test_zone_shrinks_minimum():
    arena = ProceduralArena(arena_size=100.0)
    assert arena.safe_zone_radius == 70.0

    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 60.0

    # Big delta
    arena.update_zone(2, 10.0)
    assert arena.safe_zone_radius == 0.0  # Clamped to 50.0

    arena.update_zone(3, 10.0)
    assert arena.safe_zone_radius == 0.0
