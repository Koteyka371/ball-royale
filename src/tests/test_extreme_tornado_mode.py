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

class MockBall:
    def __init__(self, id, mass):
        self.id = id
        self.mass = mass
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0

def test_extreme_tornado_mode():
    world = MockWorld()
    mode = GAME_MODES["extreme_tornado"]

    heavy_ball = MockBall(1, 2.0)
    light_ball = MockBall(2, 0.5)
    balls = [heavy_ball, light_ball]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 3
    tornado = world.arena.hazards[0]

    # Place tornado at center
    tornado.x = 500.0
    tornado.y = 500.0

    # Place balls slightly off center but within radius
    heavy_ball.x = 500.0 + 10.0
    heavy_ball.y = 500.0
    light_ball.x = 500.0 + 10.0
    light_ball.y = 500.0

    heavy_ball.vx = 0.0
    heavy_ball.vy = 0.0
    light_ball.vx = 0.0
    light_ball.vy = 0.0

    # Tick mode
    mode.tick(world, balls, delta=0.016)

    # Assert they got pushed
    assert heavy_ball.vx > 0
    assert light_ball.vx > 0

    # Assert light ball got pushed harder
    assert light_ball.vx > heavy_ball.vx

    # Check that tornado bounced and moved
    tornado.x = 10.0
    tornado.vx = -500.0
    tornado.y = 500.0
    tornado.vy = 0.0

    # Fast forward a bit
    for _ in range(10):
        mode.tick(world, balls, delta=0.016)

    assert tornado.vx > 0 # Bounced off left wall

    # Ensure speed limit
    tornado.vx = 1000.0
    tornado.vy = 1000.0
    mode.tick(world, balls, delta=0.016)
    speed = math.hypot(tornado.vx, tornado.vy)
    # The max speed per component should be bounded since total speed is capped to 300
    assert speed <= 300.1
