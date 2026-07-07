import pytest
from ai.game_modes import HardpointMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, bid, ball_type="warrior"):
        self.id = bid
        self.ball_type = ball_type
        self.alive = True
        self.x = 500
        self.y = 500
        self.time_since_death = 0.0
        self.team = None

def test_hardpoint_setup():
    mode = HardpointMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]
    mode.setup(world, balls)

    # Check teams were assigned
    assert balls[0].team == "Red"
    assert balls[1].team == "Red"
    assert balls[2].team == "Blue"
    assert balls[3].team == "Blue"

    # Check scores were initialized
    assert mode.team_scores["Red"] == 0.0
    assert mode.team_scores["Blue"] == 0.0

    # Check points generated
    assert len(mode.points) == 3

def test_hardpoint_scoring():
    mode = HardpointMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]
    mode.setup(world, balls)

    # Set all points to origin so balls can be in them easily
    for p in mode.points:
        p["x"] = 500
        p["y"] = 500
        p["radius"] = 150

    # All balls are at 500,500. So both Red and Blue have 2 balls.
    # Scores shouldn't increase because they are tied.
    mode.tick(world, balls, delta=1.0)

    assert mode.team_scores["Red"] == 0.0
    assert mode.team_scores["Blue"] == 0.0

    # Now kill one Blue ball
    balls[3].alive = False

    # Now Red has 2 balls in, Blue has 1. Red should score.
    # Since there are 3 points and all are at 500,500, Red is dominating ALL 3 points.
    mode.tick(world, balls, delta=1.0)

    assert mode.team_scores["Red"] == 30.0 # 10.0 per point
    assert mode.team_scores["Blue"] == 0.0

def test_hardpoint_check_winner():
    mode = HardpointMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]
    balls[0].team = "Red"
    balls[1].team = "Blue"
    mode.setup(world, balls)

    assert mode.check_winner(world, balls) is None

    mode.team_scores["Blue"] = 1000.0
    assert mode.check_winner(world, balls) == "Blue"
