import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from arena.arena_types import WinterArena, SummerArena

def test_winter_arena_weather_event():
    arena = WinterArena()
    initial_hazard_count = len(arena.hazards)

    # Mock random to always trigger the event
    import random
    original_random = random.random
    random.random = lambda: 0.1

    try:
        arena.update_zone(180, 0.1)
    finally:
        random.random = original_random

    # Check if blizzard triggered
    # The blizzard event adds 5 ice_patch hazards
    # Since other hazards might be cleaned up, we specifically check for new ice patches
    ice_patches_after = sum(1 for h in arena.hazards if getattr(h, "kind", "") == "ice_patch")
    assert ice_patches_after > 0

def test_summer_arena_weather_event():
    arena = SummerArena()

    # Mock random to always trigger the event
    import random
    original_random = random.random
    random.random = lambda: 0.1

    try:
        arena.update_zone(180, 0.1)
    finally:
        random.random = original_random

    # Check if heatwave triggered
    # The heatwave event adds 3 fire_zone hazards
    fire_zones = sum(1 for h in arena.hazards if getattr(h, "kind", "") == "fire_zone")
    assert fire_zones == 3
