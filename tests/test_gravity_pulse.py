from unittest.mock import Mock
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 500
        self.gravity = 0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.current_tick = 0

class MockHazard:
    def __init__(self):
        self.kind = "gravity_pulse"
        self.x = 500
        self.y = 500
        self.radius = 300
        self.pull_strength = 100
        self.id = 1
        self.active = True

class MockBall:
    def __init__(self):
        self.x = 400
        self.y = 500
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.radius = 10
        self.alive = True
        self.hp = 100
        self.team = "blue"

def test_gravity_pulse_speed_away():
    world = MockWorld()
    hazard = MockHazard()
    world.arena.hazards.append(hazard)

    ball = MockBall()
    ball.x = 400
    ball.y = 500
    ball.vx = -100 # moving away
    ball.vy = 0
    world.balls.append(ball)

    action = Action(ball, world)

    action.execute("flee", 1.0)

    assert ball.speed == 50.0

def test_gravity_pulse_speed_towards():
    world = MockWorld()
    hazard = MockHazard()
    world.arena.hazards.append(hazard)

    ball = MockBall()
    ball.x = 400
    ball.y = 500
    ball.vx = 100 # moving towards
    ball.vy = 0
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("flee", 1.0)

    assert ball.speed == 150.0
