import pytest
from ai.game_modes import ToxicSludgeMutatorMode

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0

class MockArena:
    def __init__(self):
        self.hazards = [
            MockHazard("lava"),
            MockHazard("spikes"),
            MockHazard("black_hole"),
            MockHazard("spike_trap"),
        ]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0

def test_toxic_sludge_mutator_setup():
    mode = ToxicSludgeMutatorMode()
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    mode.setup(world, balls)

    hazards = world.arena.hazards
    assert hazards[0].kind == "toxic_sludge"
    assert hazards[1].kind == "toxic_sludge"
    assert hazards[2].kind == "black_hole" # Should not be replaced
    assert hazards[3].kind == "toxic_sludge"
