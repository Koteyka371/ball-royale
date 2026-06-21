import pytest
from src.arena.arena_types import get_arena, BattleRoyaleShrinkingZoneArena

def test_battle_royale_shrinking_zone_arena():
    arena = get_arena("battle_royale_shrinking_zone", arena_size=2000.0)
    assert isinstance(arena, BattleRoyaleShrinkingZoneArena)
    assert arena.safe_zone_radius == 1400.0
    assert arena.safe_zone_center == (1000.0, 1000.0)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8

    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 1390.0
    arena.update_zone(2, 2.0)
    assert arena.safe_zone_radius == 1370.0
