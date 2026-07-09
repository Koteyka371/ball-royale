import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = 100.0
        self.base_speed = 100.0
        self.alive = True
        self.traits = []

def test_physics_anomaly_mode():
    assert "physics_anomaly_event" in GAME_MODES
    mode = GAME_MODES["physics_anomaly_event"]
    world = MockWorld()

    b1 = MockBall(400, 500, 100, 0)  # Moving towards center (500, 500)
    b2 = MockBall(600, 500, 100, 0)  # Moving away from center
    b3 = MockBall(100, 100, 100, 0)  # Outside anomaly radius

    mode.setup(world, [b1, b2, b3])

    # After setup, base speed may have been mutated by global season mutators
    setup_speed_b1 = b1.speed
    setup_speed_b2 = b2.speed
    setup_speed_b3 = b3.speed

    # Store old velocities
    old_b1_vy = b1.vy
    old_b2_vy = b2.vy

    mode.tick(world, [b1, b2, b3], 0.1)

    # b1 moves towards center, so its speed should increase relative to setup speed
    assert b1.speed > setup_speed_b1

    # b2 moves away from center, so its speed should decrease relative to setup speed
    assert b2.speed < setup_speed_b2

    # b3 is outside, so its speed should be unaffected
    assert b3.speed == setup_speed_b3

    # Check curvature. b1 velocity should have a perpendicular component added
    assert b1.vy != old_b1_vy
    assert b2.vy != old_b2_vy
