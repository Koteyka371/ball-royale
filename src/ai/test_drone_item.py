import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, team="A"):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = team
        self.ball_type = "normal"
        self.hp = 50.0
        self.max_hp = 100.0
        self.alive = True
        self.has_drone = False

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls or []
        self.time = 0.0

def test_drone_drains_health_and_heals():
    ball = MockBall(x=0, y=0, team="A")
    ball.has_drone = True

    enemy = MockBall(x=10, y=10, team="B")
    enemy.id = 2
    enemy.hp = 100.0

    world = MockWorld([ball, enemy])
    action = Action(ball, world)

    # Run a tick
    action.execute("idle", 1.0)

    # Enemy should lose 5 hp, ball should heal 5 hp
    assert enemy.hp == 95.0
    assert ball.hp == 55.0

def test_drone_out_of_range():
    ball = MockBall(x=0, y=0, team="A")
    ball.has_drone = True

    enemy = MockBall(x=200, y=200, team="B")
    enemy.id = 2
    enemy.hp = 100.0

    world = MockWorld([ball, enemy])
    action = Action(ball, world)

    # Run a tick
    action.execute("idle", 1.0)

    # Enemy out of range (150), so no drain
    assert enemy.hp == 100.0
    assert ball.hp == 50.0
