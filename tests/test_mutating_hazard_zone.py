import pytest
from ai.game_modes import GAME_MODES

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
        self.x = x
        self.y = y
        self.radius = 10
        self.is_alive = True
        self.speed = 100.0
        self.mass = 10.0
        self.damage_multiplier = 1.0

def test_mutating_hazard_zone():
    mode = GAME_MODES["mutating_hazard_zone"]

    world = MockWorld()
    b1 = MockBall(500, 500) # inside
    b2 = MockBall(100, 100) # outside
    balls = [b1, b2]

    mode.setup(world, balls)
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]

    assert hazard.x == 500
    assert hazard.y == 500
    assert hazard.radius == 200

    # Tick with large delta to trigger mutation
    b2_initial_speed = b2.speed
    b1_initial_speed = b1.speed
    mode.tick(world, balls, delta=3.1)

    # Due to base tick effects, we check if speed diverged significantly or other properties mutated
    b2_speed_diff = abs(b2.speed - b2_initial_speed)
    b1_speed_diff = abs(b1.speed - b1_initial_speed)

    mutated = (b1_speed_diff > 0.001 and abs(b1_speed_diff - b2_speed_diff) > 0.001) or b1.mass != 10.0 or b1.damage_multiplier != 1.0
    assert mutated, "Ball inside hazard should mutate"

    # Check if b2 did not mutate its mass or damage
    assert b2.mass == 10.0
    assert b2.damage_multiplier == 1.0
