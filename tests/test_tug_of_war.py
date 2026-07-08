import pytest
from ai.game_modes import TugOfWarMode

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
    def __init__(self, team="Neutral", x=0, y=0, ball_type="basic"):
        self.team = team
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.alive = True
        self.speed = 10.0
        self.base_speed = 10.0
        self.max_hp = 100.0
        self.hp = 100.0

def test_tug_of_war_setup():
    mode = TugOfWarMode()
    world = MockWorld()
    balls = [MockBall(ball_type="brawler"), MockBall(ball_type="sniper")]

    mode.setup(world, balls)

    assert len(balls) == 3 # Payload added
    payload = balls[2]
    assert payload.ball_type == "payload"
    assert payload.x == 500.0
    assert payload.y == 500.0

    assert balls[0].team == "Red"
    assert balls[1].team == "Blue"

def test_tug_of_war_tick_movement():
    mode = TugOfWarMode()
    world = MockWorld()
    balls = [MockBall(ball_type="brawler", x=500.0, y=500.0), MockBall(ball_type="sniper", x=100.0, y=100.0)]
    mode.setup(world, balls)

    # Red is close, Blue is far
    mode.tick(world, balls, 1.0)

    payload = balls[2]
    assert payload.x > 500.0 # Red pushes towards Blue goal (right)

def test_tug_of_war_winner():
    mode = TugOfWarMode()
    world = MockWorld()
    balls = [MockBall(ball_type="brawler")]
    mode.setup(world, balls)

    mode.payload.x = 950.0
    assert mode.check_winner(world, balls) == "Red"

    mode.payload.x = 50.0
    assert mode.check_winner(world, balls) == "Blue"

    mode.payload.x = 550.0
    mode.timer = 0
    assert mode.check_winner(world, balls) == "Red"
