import sys
import math
import pytest
sys.path.append('src')

from ai.game_modes import ExtremeWeatherMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockHazard:
    def __init__(self, kind, target_id=None):
        self.kind = kind
        self.target_id = target_id

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, ball_type, traits, x, y, vx, vy):
        self.id = id
        self.ball_type = ball_type
        self.traits = traits
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True

def test_magnetic_storm_weather():
    mode = ExtremeWeatherMode()
    mode.current_weather = "magnetic_storm"

    world = MockWorld()
    h1 = MockHazard("tracking_projectile", 123)
    h2 = MockHazard("fireball", 123)
    world.arena.hazards = [h1, h2]

    b1 = MockBall(1, "metal_drone", [], 100, 100, 0, 0)
    b2 = MockBall(2, "normal", ["metal"], 150, 100, 0, 0)
    b3 = MockBall(3, "normal", [], 200, 100, 0, 0)
    balls = [b1, b2, b3]

    mode.tick(world, balls, delta=0.1)

    # Assert pull
    assert b1.vx > 0, "b1 should be pulled towards b2 (right)"
    assert b2.vx < 0, "b2 should be pulled towards b1 (left)"
    assert b3.vx == 0, "b3 shouldn't be affected"

    # Assert tracking projectile disabled
    assert world.arena.hazards[0].kind == "projectile"
    assert getattr(world.arena.hazards[0], 'target_id', 123) == None
    assert world.arena.hazards[1].kind == "fireball"
