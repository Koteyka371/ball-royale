import pytest
from ai.game_modes import SharedTugOfWarMode

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
        self.speed = 10.0
        self.base_speed = 10.0
        self.max_hp = 100.0
        self.hp = 100.0

def test_shared_tug_of_war():
    mode = SharedTugOfWarMode()
    world = MockWorld()
    balls = [MockBall(ball_type="brawler")]

    mode.setup(world, balls)
    assert mode.scores == {"Red": 0.0, "Blue": 0.0}

    mode.payload.x = 600.0  # Payload is right of center (500.0)
    mode.tick(world, balls, 0.1)

    # Red scores if px > center_x
    assert mode.scores["Red"] == 0.1
    assert mode.scores["Blue"] == 0.0

    mode.payload.x = 400.0  # Payload is left of center (500.0)
    mode.tick(world, balls, 0.1)

    # Blue scores if px < center_x
    assert mode.scores["Red"] == 0.1
    assert mode.scores["Blue"] == 0.1

    # Fast forward to end of match
    mode.timer = 0.0
    mode.scores["Red"] = 10.0
    mode.scores["Blue"] = 5.0

    assert mode.check_winner(world, balls) == "Red"
