import pytest
from arena.arena_types import SummerArena, WinterArena, AutumnArena, LavaArena, NeonArena

def test_summer_arena():
    arena = SummerArena()
    assert getattr(arena, "is_heatwave", False) is True
    # Test hazards
    sun_flares = [h for h in arena.hazards if getattr(h, "kind", "") == "sun_flare"]
    sand_traps = [h for h in arena.hazards if getattr(h, "kind", "") == "sand_trap"]
    assert len(sun_flares) == 4
    assert len(sand_traps) == 5

def test_winter_arena():
    arena = WinterArena()
    assert getattr(arena, "is_snowing", False) is True
    # Test hazards
    ice_patches = [h for h in arena.hazards if getattr(h, "kind", "") == "ice_patch"]
    snowman_decoys = [h for h in arena.hazards if getattr(h, "kind", "") == "snowman_decoy"]
    assert len(ice_patches) == 5
    assert len(snowman_decoys) == 3

def test_autumn_arena():
    arena = AutumnArena()
    assert getattr(arena, "is_windy", False) is True

def test_lava_arena():
    arena = LavaArena()
    assert getattr(arena, "is_lava_theme", False) is True

def test_neon_arena():
    arena = NeonArena()
    assert getattr(arena, "is_neon_theme", False) is True
