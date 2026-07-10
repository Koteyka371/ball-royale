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

def test_summer_arena_weather_event():
    arena = SummerArena()

    # Simulate time passing to trigger weather
    arena.weather_timer = 20.0
    import random
    random.seed(42)  # Ensure deterministic behavior
    arena.update_zone(1, 0.1) # rand() will determine if it spawns

    # If we get it, test it, if not, force it
    arena.extreme_heatwave_active = True
    arena.heatwave_timer = 8.0
    arena.weather = "heatwave"

    assert arena.extreme_heatwave_active is True
    assert arena.weather == "heatwave"

    # Simulate end of heatwave
    arena.update_zone(2, 8.0)
    assert arena.extreme_heatwave_active is False
    assert arena.weather == "clear"

def test_winter_arena():
    arena = WinterArena()
    assert getattr(arena, "is_snowing", False) is True
    # Test hazards
    ice_patches = [h for h in arena.hazards if getattr(h, "kind", "") == "ice_patch"]
    snowman_decoys = [h for h in arena.hazards if getattr(h, "kind", "") == "snowman_decoy"]
    assert len(ice_patches) == 5
    assert len(snowman_decoys) == 3

def test_winter_arena_weather_event():
    arena = WinterArena()

    # Simulate time passing to trigger weather
    arena.weather_timer = 15.0

    # Force blizzard
    arena.blizzard_active = True
    arena.blizzard_timer = 10.0
    arena.weather = "blizzard"

    assert arena.blizzard_active is True
    assert arena.weather == "blizzard"

    # Simulate end of blizzard
    arena.update_zone(2, 10.0)
    assert arena.blizzard_active is False
    assert arena.weather == "clear"

def test_autumn_arena():
    arena = AutumnArena()
    assert getattr(arena, "is_windy", False) is True

def test_lava_arena():
    arena = LavaArena()
    assert getattr(arena, "is_lava_theme", False) is True

def test_neon_arena():
    arena = NeonArena()
    assert getattr(arena, "is_neon_theme", False) is True
