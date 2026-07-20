import sys
import pytest
sys.path.append('src')
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=100.0, y=100.0):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.ball_type = "test_ball"
        self.stamina = 100.0
        self.team = "team_a"

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = 0.0
        self.active = True
        self.duration = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.temperature = 20.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.width = 1000
        self.height = 1000

def test_orbital_debris_push_effect():
    world = MockWorld()
    ball = MockBall(x=100.0, y=100.0)
    world.balls = [ball]

    debris = MockHazard("orbital_debris", x=98.0, y=100.0, radius=40.0)
    world.arena.hazards.append(debris)

    action = Action(ball, world)

    # Run a full tick which should trigger the hazard loop and apply the push
    action.execute("offensive", 0.1)

    # In action.py:
    # dx = 100 - 98 = 2
    # dy = 100 - 100 = 0
    # dist = 2.0
    # nx = 2 / 2 = 1.0, ny = 0
    # push_strength = 200.0 * 0.1 = 20.0
    # x += 20.0 -> 120.0 (plus any other movement)

    assert ball.x > 105.0 # definitely moved right
