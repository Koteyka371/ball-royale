import pytest
from ai.game_modes import GAME_MODES
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, id, x, y, vx, vy):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_inverse_movement_zone():
    mode = GAME_MODES["inverse_movement_zone"]

    world = MockWorld()

    # Trigger a spawn
    mode.tick(world, [], delta=16.0)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "inverse_movement_zone"
    assert hazard.radius == 150.0

    # Create a ball inside the hazard
    b1 = MockBall(1, hazard.x, hazard.y, 100.0, 50.0)
    # Create a ball outside the hazard
    b2 = MockBall(2, hazard.x + 200, hazard.y, 100.0, 50.0)

    balls = [b1, b2]

    initial_b1_x = b1.x
    initial_b1_y = b1.y
    initial_b2_x = b2.x
    initial_b2_y = b2.y

    # Tick with delta 0.1
    mode.tick(world, balls, delta=0.1)

    # b1 is inside, so it should have moved backwards by (vx * 2 * delta) according to our logic
    # In tick(): b.x -= b.vx * delta * 2
    assert b1.x < initial_b1_x
    assert b1.y < initial_b1_y
    assert b1.x == initial_b1_x - (100.0 * 0.1 * 2)

    # b2 is outside, its position should remain unchanged by the mode
    assert b2.x == initial_b2_x
    assert b2.y == initial_b2_y
