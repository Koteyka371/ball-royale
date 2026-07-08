import pytest
from arena.procedural_arena import ProceduralArena, Hazard

def test_temperature_ice_patch_melting():
    arena = ProceduralArena(num_rooms=1, seed=42)
    arena.hazards = []

    # 20.0 temperature
    arena.temperature = 20.0

    h = Hazard(id=1, x=100, y=100, radius=50.0, kind="ice_patch", damage=0.0)
    h.duration = 20.0
    arena.hazards.append(h)

    # Simulate time passing, it should reduce duration by 20.0 * 0.1 * 1.0 = 2.0
    arena.update_zone(0, 1.0)

    assert h.duration == 18.0
    assert h.kind == "ice_patch"

def test_temperature_ice_patch_melting_to_puddle():
    arena = ProceduralArena(num_rooms=1, seed=42)
    arena.hazards = []

    # Very high temperature
    arena.temperature = 100.0

    h = Hazard(id=1, x=100, y=100, radius=50.0, kind="ice_patch", damage=0.0)
    h.duration = 5.0
    arena.hazards.append(h)

    # Simulate time passing, it should reduce duration by 100.0 * 0.1 * 1.0 = 10.0
    # 5.0 - 10.0 = -5.0 <= 0, so it becomes a puddle
    arena.update_zone(0, 1.0)

    assert h.kind == "puddle"
    assert h.duration == 20.0 # Resets duration

def test_temperature_puddle_drying():
    arena = ProceduralArena(num_rooms=1, seed=42)
    arena.hazards = []

    # High temperature
    arena.temperature = 50.0

    h = Hazard(id=1, x=100, y=100, radius=50.0, kind="puddle", damage=0.0)
    h.duration = 4.0
    arena.hazards.append(h)

    # Reduce by 50 * 0.1 * 1 = 5.0
    arena.update_zone(0, 1.0)

    assert h.active == False # Dried out

def test_temperature_puddle_freezing():
    arena = ProceduralArena(num_rooms=1, seed=42)
    arena.hazards = []

    # Negative temperature
    arena.temperature = -50.0

    h = Hazard(id=1, x=100, y=100, radius=50.0, kind="puddle", damage=0.0)
    h.duration = 4.0
    arena.hazards.append(h)

    # Reduce by 50 * 0.1 * 1 = 5.0
    arena.update_zone(0, 1.0)

    assert h.kind == "ice_patch"
    assert h.duration == 20.0

def test_temperature_fire_melting():
    arena = ProceduralArena(num_rooms=1, seed=42)
    arena.hazards = []
    arena.temperature = 0.0 # No ambient melting

    h1 = Hazard(id=1, x=100, y=100, radius=50.0, kind="ice_patch", damage=0.0)
    h1.duration = 20.0
    arena.hazards.append(h1)

    h2 = Hazard(id=2, x=120, y=120, radius=50.0, kind="fire_zone", damage=0.0)
    arena.hazards.append(h2)

    # The fire_zone overlaps with the ice_patch, it should melt instantly
    arena.update_zone(0, 1.0)

    assert h1.kind == "puddle"
    assert h1.duration == 20.0
