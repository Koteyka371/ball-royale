import pytest
from src.ai.game_modes import GAME_MODES, PolarityHazardMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.radius = 15.0

def test_polarity_hazard():
    mode = GAME_MODES["polarity_hazard"]
    world = MockWorld()
    b1 = MockBall(500, 500)
    b2 = MockBall(520, 500)
    b3 = MockBall(500, 520)
    balls = [b1, b2, b3]

    # Fast forward to trigger spawn
    for _ in range(1000):
        mode.tick(world, balls, delta=0.016)

    assert len(world.arena.hazards) > 0
    hazard = world.arena.hazards[0]
    assert hazard.kind == "polarity_hazard"

    # Move ball into hazard
    b1.x = hazard.x
    b1.y = hazard.y
    b2.x = hazard.x + 10
    b2.y = hazard.y
    b3.x = 900
    b3.y = 900

    # Process tick to apply hazard effect
    mode.tick(world, balls, delta=0.016)

    # b1 and b2 should be toggled
    assert getattr(b1, "polarity_cooldown", 0) > 0
    assert getattr(b2, "polarity_cooldown", 0) > 0
    assert getattr(b1, "polarity", 1) == -1

    # Force b1 and b2 to have opposite polarities and be close
    b1.polarity = 1
    b2.polarity = -1
    b1.x = 500
    b1.y = 500
    b2.x = 510
    b2.y = 500
    b1.vx = 0
    b2.vx = 0

    mode.tick(world, balls, delta=0.016)
    # Opposite polarities attract -> b1 vx should be > 0, b2 vx should be < 0
    assert b1.vx > 0
    assert b2.vx < 0

    # Force b1 and b2 to have same polarities and be close
    b1.polarity = 1
    b2.polarity = 1
    b1.x = 500
    b1.y = 500
    b2.x = 510
    b2.y = 500
    b1.vx = 0
    b2.vx = 0

    mode.tick(world, balls, delta=0.016)
    # Same polarities repel -> b1 vx should be < 0, b2 vx should be > 0
    assert b1.vx < 0
    assert b2.vx > 0
