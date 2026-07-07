import pytest
from ai.game_modes import CrossfireMode

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.dead_balls = []

class MockBall:
    def __init__(self, x=0.0, y=0.0, vx=0.0, vy=0.0, alive=True, ball_type="player", radius=15.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = alive
        self.ball_type = ball_type
        self.radius = radius
        self.team = None

def test_crossfire_mode_setup():
    mode = CrossfireMode()
    world = MockWorld(MockArena(width=1000, height=1000))
    balls = [MockBall(alive=True) for _ in range(4)]

    mode.setup(world, balls)

    # Half left, half right
    teams = [b.team for b in balls]
    assert teams.count("team_left") == 2
    assert teams.count("team_right") == 2

    for b in balls:
        if b.team == "team_left":
            assert b.x < 500.0
        elif b.team == "team_right":
            assert b.x > 500.0

def test_crossfire_mode_tick():
    mode = CrossfireMode()
    world = MockWorld(MockArena(width=1000, height=1000))

    # Left team ball crossing line (center = 500)
    b_left = MockBall(x=500.0, vx=100.0) # Will cross with radius 15
    b_left.team = "team_left"

    # Right team ball crossing line
    b_right = MockBall(x=500.0, vx=-100.0) # Will cross with radius 15
    b_right.team = "team_right"

    balls = [b_left, b_right]

    mode.tick(world, balls, delta=0.016)

    # Left ball pushed back
    assert b_left.x == 500.0 - 15.0
    assert b_left.vx == -50.0  # -abs(100) * 0.5

    # Right ball pushed back
    assert b_right.x == 500.0 + 15.0
    assert b_right.vx == 50.0  # abs(-100) * 0.5
