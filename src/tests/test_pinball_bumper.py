import pytest
from ai.action import Action
import math
import random

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
        self.boundary_offsets = {"top":0,"bottom":0,"left":0,"right":0}
        self.platforms = []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = []
        self.projectiles = []
        self.tick = 0

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 20.0
        self.duration = 10.0
        self.id = 1
        self.active = True

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.base_speed = 50.0
        self.speed = 50.0
        self.mass = 1.0
        self.base_mass = 1.0
        self.team = "blue"

def test_pinball_bumper():
    # Make random predictable
    random.seed(42)
    ball = MockBall(1, 100.0, 100.0)
    bumper = MockHazard(105.0, 105.0, "pinball_bumper")
    bumper.radius = 20.0
    world = MockWorld(MockArena([bumper]), [ball])
    action = Action(ball, world)

    # Original vx and vy
    ball.vx = 0.0
    ball.vy = 0.0

    action.execute("idle", 0.016)

    # Check that ball bounced
    assert ball.vx != 0.0 or ball.vy != 0.0

    print("Pinball bumper bounce works: vx", ball.vx, "vy", ball.vy)
    assert abs(ball.vx) > 200.0 or abs(ball.vy) > 200.0

if __name__ == '__main__':
    test_pinball_bumper()
