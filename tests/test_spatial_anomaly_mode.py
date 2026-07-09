import pytest
import math
from ai.game_modes import SpatialAnomalyMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
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
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.time_since_death = 0.0
        self.weather_immunity_timer = 0.0

class MockHazard:
    def __init__(self, x, y, vx, vy, kind="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.kind = kind

def test_spatial_anomaly_ball_speed_towards_center():
    # Anomaly is at 500, 500
    # Ball is at 300, 500. Moving right (towards center).
    world = MockWorld()
    mode = SpatialAnomalyMode()
    ball = MockBall(300, 500, 100.0, 0.0)

    mode.tick(world, [ball], delta=1.0)

    # Moving directly towards center -> dot product is 1.0 -> speed_mult = 1.5
    assert ball.speed > 100.0
    assert abs(ball.speed - 150.0) < 0.1

def test_spatial_anomaly_ball_speed_away_from_center():
    # Anomaly is at 500, 500
    # Ball is at 300, 500. Moving left (away from center).
    world = MockWorld()
    mode = SpatialAnomalyMode()
    ball = MockBall(300, 500, -100.0, 0.0)

    mode.tick(world, [ball], delta=1.0)

    # Moving directly away -> dot product is -1.0 -> speed_mult = 0.5
    assert ball.speed < 100.0
    assert abs(ball.speed - 50.0) < 0.1

def test_spatial_anomaly_curvature():
    # Anomaly is at 500, 500
    # Ball is at 300, 500. Moving right (towards center).
    # Tangent vector should curve it up or down.
    # dx = -200, dy = 0. tx = 0, ty = -1.
    world = MockWorld()
    mode = SpatialAnomalyMode()
    ball = MockBall(300, 500, 100.0, 0.0)

    orig_vy = ball.vy
    mode.tick(world, [ball], delta=1.0)

    # ty = dx / dist = -200/200 = -1
    # vy should become negative (curve upwards in screen coords)
    assert ball.vy < 0

def test_spatial_anomaly_hazard_curvature():
    world = MockWorld()
    mode = SpatialAnomalyMode()

    # Hazard is at 300, 500. Moving right.
    hazard = MockHazard(300, 500, 100.0, 0.0)
    world.arena.hazards.append(hazard)

    mode.tick(world, [], delta=1.0)

    # Hazards curve faster
    assert hazard.vy < 0
    # Speed should be maintained
    assert abs(math.hypot(hazard.vx, hazard.vy) - 100.0) < 0.1
