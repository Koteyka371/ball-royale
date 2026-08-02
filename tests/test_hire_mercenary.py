import pytest
from ai.action import Action

class MockBall:
    def __init__(self, _id, x, y):
        self.id = _id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.alive = True
        self.team = "team1"
        self.ball_type = "normal"
        self.skill_points = 100
        self.skill = "hire_mercenary"
        self.skill_timer = 0.0
        self.perception_radius = 500.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.tick = 0
        self.events = []

def test_hire_mercenary():
    world = MockWorld()
    ball1 = MockBall(1, 100, 100)
    ball2 = MockBall(2, 120, 100)
    ball2.team = "team2"
    ball2.ball_type = "enemy"

    world.balls = [ball1, ball2]

    action = Action(ball1, world)

    assert ball2.team == "team2"
    assert ball1.skill_points == 100

    action._use_skill()

    assert ball2.team == "team1"
    assert getattr(ball2, "is_mercenary", False) == True
    assert getattr(ball2, "mercenary_timer", 0.0) == 15.0
    assert getattr(ball2, "original_team", "") == "team2"
    assert ball1.skill_points == 50

def test_mercenary_timer():
    world = MockWorld()
    ball1 = MockBall(1, 100, 100)
    ball1.is_mercenary = True
    ball1.mercenary_timer = 0.5
    ball1.original_team = "team2"
    ball1.team = "team1"

    world.balls = [ball1]

    action = Action(ball1, world)

    action.execute("attack", 0.6)

    assert ball1.is_mercenary == False
    assert ball1.team == "team2"
