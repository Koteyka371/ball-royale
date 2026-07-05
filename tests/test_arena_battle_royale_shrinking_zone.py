import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import BattleRoyaleShrinkingZoneArena

def test_battle_royale_shrinking_zone_update():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=1000.0, num_rooms=5, seed=42)
    # Default start radius is 700.0 based on ProceduralArena base
    assert arena.safe_zone_radius == 700.0

    # Tick 1
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 685.0 # 700 - 15 * 1

    # Same tick shouldn't update
    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 685.0

    # Next tick should shrink
    arena.update_zone(2, 2.0)
    assert arena.safe_zone_radius == 655.0 # 685 - 15 * 2

def test_battle_royale_shrinking_zone_minimum():
    arena = BattleRoyaleShrinkingZoneArena(arena_size=100.0, num_rooms=5, seed=42)
    assert arena.safe_zone_radius == 70.0

    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 55.0 # 70 - 15

    # Clamp to min size 50.0
    arena.update_zone(2, 10.0)
    assert arena.safe_zone_radius == 0.0
