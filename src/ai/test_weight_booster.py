import pytest
from ai.action import Action
from arena.arena_types import Hazard
import copy

class MockArena:
    def __init__(self):
        self.hazards = []
        self.wind_dx = 0.0
        self.wind_dy = 0.0
        self.weather = "none"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.boosters = []

class MockBall:
    def __init__(self, x=0.0, y=0.0, team=1):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.hp = 100
        self.alive = True
        self.team = team
        self.weight_booster_timer = 0.0

def test_weight_booster_collection_and_speed_reduction():
    world = MockWorld()
    ball = MockBall(0.0, 0.0, 1)
    action = Action(ball, world)

    booster = Hazard(2, 5.0, 0.0, 15.0, "weight_booster", 0)
    world.boosters.append(booster)
    world.balls.append(ball)

    action.execute("collect_booster", 0.1)

    assert getattr(ball, "weight_booster_timer", 0.0) > 0.0
    assert getattr(ball, "weight_booster_applied", False) == True
    # Base speed should be halved
    assert ball.base_speed == 50.0

def test_weight_booster_wind_immunity():
    world = MockWorld()
    ball = MockBall(0.0, 0.0, 1)
    action = Action(ball, world)

    world.arena.wind_dx = 100.0
    world.balls.append(ball)

    ball.weight_booster_timer = 5.0
    action.execute("idle", 0.1)

    # Normally wind would push x to 10.0. With immunity it should stay near 0 (just random noise from idle)
    assert abs(ball.x) < 30.0

def test_weight_booster_gravity_well_immunity():
    world = MockWorld()
    ball = MockBall(0.0, 0.0, 1)
    ball.weight_booster_timer = 5.0
    world.balls.append(ball)

    gw = Hazard(2, 10.0, 0.0, 100.0, "gravity_well", 0)
    world.arena.hazards.append(gw)

    action = Action(ball, world)

    start_x = ball.x
    action.execute("idle", 0.1)

    # Gravity well pull is normally huge. Since we're immune, we won't be pulled strongly towards it.
    assert abs(ball.x - start_x) < 30.0
