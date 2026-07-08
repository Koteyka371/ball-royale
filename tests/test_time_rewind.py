import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y, hp):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.ball_type = "player"
        self.vx = 10.0
        self.vy = 20.0

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_time_rewind_mode():
    mode = GAME_MODES["time_rewind"]
    assert mode.name == "Time Rewind"

    world = MockWorld()
    ball = MockBall("b1", 10.0, 20.0, 100.0)
    balls = [ball]

    mode.rewind_timer = 0.0
    mode.history = {}

    # Simulate t=0 to t=24
    for i in range(24):
        mode.tick(world, balls, delta=1.0)

    # At t=25, ball is at 50, 60
    ball.x = 50.0
    ball.y = 60.0
    ball.hp = 80.0
    mode.tick(world, balls, delta=1.0)

    # Simulate t=26 to t=29
    for i in range(4):
        ball.x += 10.0
        ball.y += 10.0
        mode.tick(world, balls, delta=1.0)

    # At t=30, ball should rewind to state at t=25
    ball.x = 100.0
    ball.y = 110.0
    ball.hp = 50.0
    mode.tick(world, balls, delta=1.0)

    # Ball should be rewound to the state at 25.0 seconds
    assert ball.x == 50.0
    assert ball.y == 60.0
    assert ball.hp == 80.0

    # Momentum (vx, vy) should be preserved
    assert ball.vx == 10.0
    assert ball.vy == 20.0

    # History should be cleared and timer reset
    assert len(mode.history) == 0
    assert mode.rewind_timer == 0.0
