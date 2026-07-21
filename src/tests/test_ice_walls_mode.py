import pytest
from ai.game_modes import IceWallsMode

class MockArena:
    def __init__(self):
        self.boundary_states = {}
        self.boundary_health = {}
        self.boundary_offsets = {"top": 50.0, "bottom": 0.0, "left": 0.0, "right": 0.0}

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_ice_walls_mode():
    world = MockWorld()
    mode = IceWallsMode()

    # Test start
    mode.start(world, [])
    assert world.arena.boundary_states["top"] == "ice"
    assert world.arena.boundary_health["top"] == 2000.0

    # Test regeneration
    world.arena.boundary_health["top"] = 1500.0
    mode.tick(world, [], 5.0)
    assert world.arena.boundary_health["top"] == 1750.0

    # Test state regeneration
    world.arena.boundary_states["top"] = "abyss"
    mode.tick(world, [], 5.0)
    assert world.arena.boundary_states["top"] == "ice"
    assert world.arena.boundary_health["top"] == 1000.0
    assert world.arena.boundary_offsets["top"] == 0.0
