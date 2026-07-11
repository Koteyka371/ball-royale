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
        self.boosters = []
        def _get_nearby_entities(ball, radius):
            return {'boosters': [], 'hazards': [], 'enemies': []}
        self.get_nearby_entities = _get_nearby_entities

class MockEntity:
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.alive = alive

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.team = 1
        self.id = 1
        self.hp = 100
        self.inventory = ["hookshot"]

def test_hookshot_to_wall():
    world = MockWorld()
    ball = MockBall(100, 500)
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("flee", 1.0) # Hookshot logic runs during flee/defend/attack

    # Should pull towards closest wall (left wall)
    assert math.isclose(ball.x, 0.0, abs_tol=20.0)
    assert math.isclose(ball.y, 500.0, abs_tol=5.0)
    assert "hookshot" not in ball.inventory

def test_hookshot_to_entity():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    target = MockBall(600, 500)
    target.id = 2
    world.balls.append(target)

    action = Action(ball, world)
    action.execute("attack", 1.0)

    # Should pull towards target
    assert math.isclose(ball.x, 600.0, abs_tol=10) # 500 + 500 dist
    assert math.isclose(ball.y, 500.0, abs_tol=10)
    assert "hookshot" not in ball.inventory
