import pytest
from src.ai.game_modes import ToxicSludgeMutatorMode

class MockHazard:
    def __init__(self, kind, x=500, y=500, radius=30):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.id = id(self)
        self.is_toxic_sludge = False

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = [
            MockHazard("lava", 200, 200),
            MockHazard("spikes", 300, 300),
            MockHazard("wall", 400, 400)
        ]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15
        self.alive = True
        self.speed = 100.0
        self.radiation_duration = 0.0
        self.radiation_multiplier = 1.0
        self.ball_type = "player"

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

def test_toxic_sludge_mutator_replaces_hazards():
    mode = ToxicSludgeMutatorMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    # Check hazards were replaced
    assert world.arena.hazards[0].kind == "poison_cloud"
    assert getattr(world.arena.hazards[0], "is_toxic_sludge", False) == True

    assert world.arena.hazards[1].kind == "poison_cloud"
    assert getattr(world.arena.hazards[1], "is_toxic_sludge", False) == True

    # Check wall was not replaced
    assert world.arena.hazards[2].kind == "wall"
    assert getattr(world.arena.hazards[2], "is_toxic_sludge", False) == False

def test_toxic_sludge_mutator_applies_debuffs():
    mode = ToxicSludgeMutatorMode()
    world = MockWorld()

    # Ball inside sludge
    b1 = MockBall(1, 200, 200)
    # Ball outside sludge
    b2 = MockBall(2, 800, 800)
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    assert b1.radiation_duration == 10.0
    assert b1.radiation_multiplier == 1.5
    assert b1.speed == pytest.approx(b1.base_speed * 0.5)

    assert b2.radiation_duration == 0.0
    assert b2.radiation_multiplier == 1.0
    assert b2.speed == b2.base_speed
