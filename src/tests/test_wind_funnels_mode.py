import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, kind, data):
        pass

class MockBall:
    def __init__(self, x=0.0, y=0.0, alive=True):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = alive

def test_wind_funnels_mode():
    mode = GAME_MODES["wind_funnels"]
    world = MockWorld()

    # Setup mode to generate funnels
    mode.setup(world, [])
    assert len(mode.funnels) >= 3
    assert len(world.arena.hazards) == len(mode.funnels)

    # Force exactly 1 known funnel
    mode.funnels = [{
        "x1": 100.0, "y1": 100.0,
        "x2": 400.0, "y2": 100.0,
        "width": 50.0,
        "force": 1000.0,
        "dir_x": 1.0,
        "dir_y": 0.0,
        "length_sq": 90000.0
    }]
    f = mode.funnels[0]

    # Ball inside funnel (at start)
    ball_inside = MockBall(x=f["x1"], y=f["y1"])
    # Ball outside funnel (far away)
    ball_outside = MockBall(x=f["x1"] + f["width"] + 100, y=f["y1"] + f["width"] + 100)

    balls = [ball_inside, ball_outside]

    mode.tick(world, balls, 1.0)

    # Inside ball should be pushed
    assert ball_inside.vx != 0.0 or ball_inside.vy != 0.0
    assert abs(ball_inside.vx) == pytest.approx(abs(f["dir_x"] * f["force"]), rel=1e-2)
    assert abs(ball_inside.vy) == pytest.approx(abs(f["dir_y"] * f["force"]), rel=1e-2)

    # Outside ball should not be affected
    assert ball_outside.vx == 0.0
    assert ball_outside.vy == 0.0
