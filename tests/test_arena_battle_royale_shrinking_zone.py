import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import BattleRoyaleShrinkingZoneArena

def test_battle_royale_shrinking_zone_arena_generation():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=2000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 0

def test_battle_royale_shrinking_zone_arena_is_point_inside():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=2000.0)
    assert arena.is_point_inside(1000, 1000, 10)  # Center
    assert arena.is_point_inside(100, 100, 10)    # Top left corner
    assert not arena.is_point_inside(500, 100, 10) # Empty space

def test_battle_royale_shrinking_zone_update_zone():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=2000.0)
    initial_radius = arena.safe_zone_radius
    arena.update_zone(0, 1.0)
    assert arena.safe_zone_radius == initial_radius - 10.0
