import pytest
from ai.game_modes import ControlPointsMode

class MockBall:
    def __init__(self, id, ball_type="neural"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.x = 0.0
        self.y = 0.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []
        self.scores = {"Red": 0.0, "Blue": 0.0}

def test_control_points_setup():
    mode = ControlPointsMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]
    mode.setup(world, balls)

    assert balls[0].team == "Red"
    assert balls[1].team == "Blue"
    assert len(mode.points) == 3

def test_control_points_capture_and_score():
    mode = ControlPointsMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]
    mode.setup(world, balls)

    pt = mode.points[0]

    # Move Red ball inside point 1, Blue outside
    balls[0].x = pt.x
    balls[0].y = pt.y
    balls[1].x = 9999
    balls[1].y = 9999

    # Tick to accumulate progress
    for _ in range(6): # 6 * 20 * 1.0 = 120 progress -> captured
        mode.tick(world, balls, delta=1.0)

    assert pt.owner == "Red"
    assert world.scores["Red"] > 0
    assert world.scores["Blue"] == 0

def test_control_points_move():
    mode = ControlPointsMode()
    world = MockWorld()
    balls = []
    mode.setup(world, balls)

    # Initial positions
    initial_x = mode.points[0].x
    initial_y = mode.points[0].y

    # Advance time past move_interval
    mode.tick(world, balls, delta=mode.move_interval + 1.0)

    # Check if moved
    assert mode.points[0].x != initial_x or mode.points[0].y != initial_y
    event_types = [e["type"] for e in world.events]
    assert "control_points_moved" in event_types

def test_control_points_winner():
    mode = ControlPointsMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]
    mode.setup(world, balls)

    assert mode.check_winner(world, balls) is None

    world.scores["Blue"] = mode.target_score + 10.0
    assert mode.check_winner(world, balls) == "Blue"

def test_control_points_draw_on_death():
    mode = ControlPointsMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]
    mode.setup(world, balls)

    balls[0].alive = False
    balls[1].alive = False

    world.scores["Red"] = 50.0
    world.scores["Blue"] = 40.0

    assert mode.check_winner(world, balls) == "Red"
