import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.id = id(self)

class MockBall:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.alive = True
        self.radius = 10
        self.base_speed = 100.0
        self.speed = 100.0
        self.intangible = False
        self.intangible_timer = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

def test_flight_booster_collection():
    world = MockWorld()
    ball = MockBall(100.0, 100.0, "Team A")
    world.balls.append(ball)

    action = Action(ball, world)

    # Place a flight booster nearby
    booster = MockBooster(105.0, 100.0, "flight_booster")
    world.boosters.append(booster)

    # Mock _get_boosters to return our list
    action._get_boosters = lambda: world.boosters

    # Execute collection
    action._collect_booster(0.016)

    # Assert booster was collected
    assert len(world.boosters) == 0

    # Assert effects were applied
    assert getattr(ball, "flight_booster_timer", 0.0) == 5.0
    assert getattr(ball, "is_flying", False) == True
    assert getattr(ball, "is_frictionless", False) == True
    assert getattr(ball, "knockback_immune", False) == True
    assert ball.speed == ball.base_speed * 3.0

def test_flight_booster_tick_down():
    world = MockWorld()
    ball = MockBall(100.0, 100.0, "Team A")
    world.balls.append(ball)

    ball.flight_booster_timer = 0.1
    ball.is_flying = True
    ball.is_frictionless = True
    ball.knockback_immune = True
    ball.speed = ball.base_speed * 3.0

    action = Action(ball, world)

    # Tick with delta > timer
    action.execute("idle", 0.15)

    assert getattr(ball, "flight_booster_timer", 0.0) == 0.0
    assert getattr(ball, "is_flying", True) == False
    assert getattr(ball, "is_frictionless", True) == False
    assert getattr(ball, "knockback_immune", True) == False
    assert getattr(ball, "speed", 0.0) == getattr(ball, "base_speed", 2.0)
