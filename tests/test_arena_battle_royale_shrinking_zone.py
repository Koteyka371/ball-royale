from arena.arena_types import BattleRoyaleShrinkingZoneArena

def test_battle_royale_shrinking_zone_generation():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5

    # Check center room
    cx, cy = 1000.0, 1000.0
    center_room = arena.rooms[0]
    assert center_room.x == cx - 500.0
    assert center_room.y == cy - 500.0
    assert center_room.width == 1000.0
    assert center_room.height == 1000.0

def test_battle_royale_shrinking_zone_is_point_inside():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=2000.0)

    # Inside center room
    assert arena.is_point_inside(1000.0, 1000.0, 10.0)

    # Inside top-left spawn room
    assert arena.is_point_inside(150.0, 150.0, 10.0)

    # Outside
    assert not arena.is_point_inside(5.0, 5.0, 10.0)

def test_battle_royale_shrinking_zone_update_zone():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=2000.0)
    assert arena.safe_zone_radius == 1400.0  # 2000 * 0.7

    # Tick 1
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 1390.0

    # Same tick shouldn't shrink again
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 1390.0

    # Next tick should shrink
    arena.update_zone(2, 2.0)
    assert arena.safe_zone_radius == 1370.0

def test_battle_royale_shrinking_zone_shrinks_minimum():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=100.0)
    assert arena.safe_zone_radius == 70.0

    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 60.0

    # Big delta
    arena.update_zone(2, 10.0)
    assert arena.safe_zone_radius == 50.0  # Clamped to 50.0

    arena.update_zone(3, 10.0)
    assert arena.safe_zone_radius == 50.0
