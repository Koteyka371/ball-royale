import pytest
import math

# Use the full path so pytest can find it
from src.ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
    def clamp_position(self, x, y, r):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockBall:
    def __init__(self):
        self.x = 1000.0
        self.y = 1000.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.team = "A"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.hazards = []
        self.events = []

def test_stationary_wind_funnels_mode():
    mode = GAME_MODES["stationary_wind_funnels"]
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    # We'll override math.random temporarily or just let setup run
    mode.setup(world, balls)

    assert len(mode.funnels) == 4
    assert len(world.hazards) == 4

    # Set ball 0 to be exactly in the center of the first funnel
    f = mode.funnels[0]

    # Place ball 0 inside the funnel (midway along its length)
    mid_proj = f["length"] / 2
    balls[0].x = f["x"] + math.cos(f["angle"]) * mid_proj
    balls[0].y = f["y"] + math.sin(f["angle"]) * mid_proj
    balls[0].vx = 0
    balls[0].vy = 0

    # Place ball 1 far away
    balls[1].x = 0
    balls[1].y = 0
    balls[1].vx = 0
    balls[1].vy = 0

    mode.tick(world, balls, 0.1)

    # Ball 0 should have velocity applied in the direction of the funnel
    fx = math.cos(f["angle"])
    fy = math.sin(f["angle"])

    expected_vx = fx * f["force"] * 0.1
    expected_vy = fy * f["force"] * 0.1

    assert abs(balls[0].vx - expected_vx) < 1e-4
    assert abs(balls[0].vy - expected_vy) < 1e-4

    # Ball 1 should not have any velocity
    assert balls[1].vx == 0
    assert balls[1].vy == 0
