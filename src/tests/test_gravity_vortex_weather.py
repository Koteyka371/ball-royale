import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self):
        self.x = 200.0
        self.y = 200.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "normal"
        self.heavy_anchor_booster_timer = 0.0
        self.weather_immunity_timer = 0.0

def test_gravity_vortex_pulls_to_center():
    mode = GAME_MODES["extreme_weather"]
    mode.current_weather = "gravity_vortex"
    world = MockWorld()
    ball = MockBall()
    ball.x = 100.0
    ball.y = 100.0
    ball.vx = 0.0
    ball.vy = 0.0

    # 100, 100 relative to center 500, 500
    # pull is 200 * delta
    # delta = 0.1 => 20
    # dx = 400, dy = 400 => dist = 400*sqrt(2)
    # dir x = dx/dist = 1/sqrt(2) approx 0.707
    # vx += 20 * 0.707 = 14.14
    mode.tick(world, [ball], 0.1)

    assert ball.vx > 10.0
    assert ball.vy > 10.0

def test_gravity_vortex_anchor_immunity():
    mode = GAME_MODES["extreme_weather"]
    mode.current_weather = "gravity_vortex"
    world = MockWorld()
    ball = MockBall()
    ball.x = 100.0
    ball.y = 100.0
    ball.vx = 0.0
    ball.vy = 0.0
    ball.heavy_anchor_booster_timer = 5.0

    mode.tick(world, [ball], 0.1)

    assert ball.vx == 0.0
    assert ball.vy == 0.0
