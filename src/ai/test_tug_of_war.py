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
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
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

    # Place brawler exactly hitting the payload to transfer velocity
    # Payload is at (500, 500) initially.
    # Brawler radius 10, payload radius 20, sum 30.
    # Brawler at (475, 500), dist is 25 (overlapping)
    # Brawler has high vx
    brawler = MockBall(ball_type="brawler", x=475.0, y=500.0)
    brawler.vx = 1000.0

    balls = [brawler, MockBall(ball_type="sniper", x=100.0, y=100.0)]
    mode.setup(world, balls)

    # Call tick
    mode.tick(world, balls, 0.1)

    payload = balls[2]
    # The payload should have received a rightwards impulse (vx > 0) and moved right (x > 500)
    assert getattr(payload, "vx", 0.0) > 0.0
    assert payload.x > 500.0

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
