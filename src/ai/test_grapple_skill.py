import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []
        self.items = []
        self.events = []

class MockEntity:
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.alive = alive

class MockBall:
    def __init__(self, x, y, skill="grapple"):
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_cooldown = 5.0
        self.skill_timer = 0.0
        self.alive = True
        self.team = 1
        self.id = 1
        self.hp = 100

def test_grapple_to_wall():
    world = MockWorld()
    ball = MockBall(100, 500)
    world.balls.append(ball)

    action = Action(ball, world)
    action._use_skill()

    # The ball is no longer pulled to the wall, instead it swings tangentially
    assert ball.x == 100
    assert ball.y == 500.0

def test_grapple_to_entity():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    target = MockEntity(600, 500)
    world.items.append(target)

    action = Action(ball, world)
    action._use_skill()

    assert ball.x == 700.0
    assert ball.y == 500.0

def test_grapple_to_ball():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    target_ball = MockBall(600, 500)
    world.balls.append(target_ball)

    action = Action(ball, world)
    action._use_skill()

    # User is pulled
    assert ball.x == 700.0
    assert ball.y == 500.0

    # Target ball remains stationary
    assert target_ball.x == 600.0
    assert target_ball.y == 500.0

def test_grapple_to_enemy_ball():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    target_ball = MockBall(600, 500)
    target_ball.team = 2
    world.balls.append(target_ball)

    action = Action(ball, world)
    action._use_skill()

    # User remains stationary
    assert ball.x == 500.0
    assert ball.y == 500.0

    # Target ball is pulled
    assert target_ball.x == 400.0
    assert target_ball.y == 500.0
