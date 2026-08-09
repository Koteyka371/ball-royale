import sys
import os
import math
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.speed = 10.0
        self.cosmetic = "default"
        self.wind_shield_booster_timer = 0.0

class MockHazard:
    def __init__(self, kind="tornado"):
        self.id = 99
        self.kind = kind
        self.x = 100.0
        self.y = 100.0
        self.radius = 50.0
        self.duration = 10.0
        self.damage = 10.0

class MockArena:
    def __init__(self):
        self.wind_dx = 100.0
        self.wind_dy = 0.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": self.boosters}

def test_wind_shield_booster_collection():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    booster = MockHazard(kind="wind_shield_booster")
    booster.x = 100.0
    booster.y = 100.0
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("collect_booster", 0.1)

    assert ball.wind_shield_booster_timer > 0.0
    assert len(world.boosters) == 0

def test_wind_shield_booster_wind_immunity():
    ball = MockBall()
    ball.wind_shield_booster_timer = 5.0
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action._idle = lambda d: None
    action.execute("idle", 0.1)

    # Ball should not have moved from wind
    assert ball.x == 100.0
    assert ball.y == 100.0

def test_wind_shield_booster_tornado_immunity():
    ball = MockBall()
    ball.wind_shield_booster_timer = 5.0
    world = MockWorld()
    world.balls.append(ball)

    # Put a tornado slightly away to test pull
    tornado = MockHazard(kind="tornado")
    tornado.x = 120.0
    tornado.y = 100.0
    world.arena.hazards.append(tornado)

    action = Action(ball, world)
    action._idle = lambda d: None
    action.execute("idle", 0.1)

    # Ball should not have been pulled by the tornado
    assert ball.x == 100.0
    assert ball.y == 100.0

if __name__ == "__main__":
    test_wind_shield_booster_collection()
    test_wind_shield_booster_wind_immunity()
    test_wind_shield_booster_tornado_immunity()
    print("All tests passed!")

def test_wind_shield_storm_immunity():
    ball = MockBall()
    ball.wind_shield_booster_timer = 5.0

    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action._idle = lambda d: None

    world.arena.weather = "thunderstorm"
    lightning = MockHazard(kind="lightning_strike")
    lightning.x = 100.0
    lightning.y = 100.0
    world.arena.hazards.append(lightning)

    action.execute("idle", 0.1)

    # Ball should not take damage from lightning strike
    assert ball.hp == 100.0
