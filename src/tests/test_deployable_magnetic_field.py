import pytest
import math
from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, ball_type="bot"):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = ball_type

class Hazard:
    def __init__(self, x, y, r, kind):
        self.x = x
        self.y = y
        self.radius = r
        self.kind = kind

def test_magnetic_field_pulls_ball_and_payload():
    gm = GameMode()
    world = MockWorld()

    mf = Hazard(500, 500, 300, "magnetic_field")
    world.arena.hazards.append(mf)

    ball = MockBall(600, 500)
    payload = MockBall(700, 500, "payload")
    payload.is_payload = True

    balls = [ball, payload]
    gm.apply_dynamic_traits(world, balls, 1.0)

    assert ball.x < 600
    assert payload.x < 700
