import pytest
from arena.arena_types import SummerArena, WinterArena, AutumnArena, LavaArena, NeonArena

def test_summer_arena():
    arena = SummerArena()
    # It has 4 sun_flares and 5 sand_traps at start
    sun_flares = len([h for h in arena.hazards if getattr(h, "kind", "") == "sun_flare"])
    sand_traps = len([h for h in arena.hazards if getattr(h, "kind", "") == "sand_trap"])
    assert sun_flares == 4
    assert sand_traps == 5

    assert getattr(arena, "is_heatwave", False) is False
    arena.update_zone(current_tick=0, delta=30.0)
    assert getattr(arena, "is_heatwave", False) is True

    # Test hazards after event trigger
    fire_zones = len([h for h in arena.hazards if getattr(h, "kind", "") == "fire_zone"])
    assert fire_zones == 3

def test_winter_arena():
    arena = WinterArena()

    ice_patches = len([h for h in arena.hazards if getattr(h, "kind", "") == "ice_patch"])
    snowman_decoys = len([h for h in arena.hazards if getattr(h, "kind", "") == "snowman_decoy"])
    assert ice_patches >= 5
    assert snowman_decoys >= 3

    assert getattr(arena, "is_snowing", False) is False
    arena.update_zone(current_tick=0, delta=30.0)
    assert getattr(arena, "is_snowing", False) is True

    # After update_zone and event trigger, there should be more ice_patches (puddles freeze + 5 random ones added)
    new_ice_patches = len([h for h in arena.hazards if getattr(h, "kind", "") == "ice_patch"])
    assert new_ice_patches >= ice_patches

def test_autumn_arena():
    arena = AutumnArena()
    assert getattr(arena, "is_windy", False) is True

def test_lava_arena():
    arena = LavaArena()
    assert getattr(arena, "is_lava_theme", False) is True

def test_neon_arena():
    arena = NeonArena()
    assert getattr(arena, "is_neon_theme", False) is True
