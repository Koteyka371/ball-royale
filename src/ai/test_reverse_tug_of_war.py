import pytest
from ai.game_modes import ReverseTugOfWarMode

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

def test_reverse_tug_of_war_setup():
    mode = ReverseTugOfWarMode()
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

def test_reverse_tug_of_war_tick_movement():
    mode = ReverseTugOfWarMode()
    world = MockWorld()
    # Payload starts at 500, 500
    # Red is close (500, 500), Blue is far (100, 100)
    balls = [MockBall(ball_type="brawler", x=500.0, y=500.0), MockBall(ball_type="sniper", x=100.0, y=100.0)]
    mode.setup(world, balls)

    # Tick
    mode.tick(world, balls, 1.0)

    payload = balls[2]
    # In Reverse Tug of War, red is close, so the payload should move AWAY from Red (right, +x)
    assert payload.x < 500.0

    # Now let's make Blue close, Red far
    balls[0].x = 100.0
    balls[0].y = 100.0
    balls[1].x = payload.x
    balls[1].y = payload.y

    mode.tick(world, balls, 1.0)
    # Payload should move left (away from Blue, towards Red)
    assert payload.x > 450.0

def test_reverse_tug_of_war_winner():
    mode = ReverseTugOfWarMode()
    world = MockWorld()
    balls = [MockBall(ball_type="brawler")]
    mode.setup(world, balls)

    mode.payload.x = 950.0
    # Payload at Blue's goal means Red wins (Red pushed it away into Blue goal)
    assert mode.check_winner(world, balls) == "Red"

    mode.payload.x = 50.0
    # Payload at Red's goal means Blue wins
    assert mode.check_winner(world, balls) == "Blue"

    mode.payload.x = 550.0
    mode.timer = 0
    # Red pushed it further right, Red wins
    assert mode.check_winner(world, balls) == "Red"
