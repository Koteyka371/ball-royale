import pytest
from ai.game_modes import ColorTrailMode

class MockBall:
    def __init__(self, x, y, team, ball_type="basic"):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.base_speed = 100.0
        self.speed = 100.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.id = id(self)

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_color_trail_mode():
    mode = ColorTrailMode()
    world = MockWorld()

    red = MockBall(50, 50, "Red")
    blue = MockBall(200, 200, "Blue")
    balls = [red, blue]

    mode.tick(world, balls, 1.0)

    assert red.speed == 150.0
    assert red.hp == 100.0
