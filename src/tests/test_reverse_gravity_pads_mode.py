import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_reverse_gravity_pads_mode():
    world = MockWorld()
    mode = GAME_MODES["reverse_gravity_pads"]
    mode.setup(world, [])

    pads = [h for h in world.arena.hazards if h["kind"] == "reverse_gravity_pad"]
    assert len(pads) == 10
    assert pads[0]["duration"] == 9999.0
    assert 0 <= pads[0]["x"] <= 1000
    assert 0 <= pads[0]["y"] <= 1000
