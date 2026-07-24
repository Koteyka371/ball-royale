import pytest
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.is_snowing = False
        self.is_ice = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []
        self.projectiles = []
        self.teams = {1: {"score": 0}}
        self.game_mode = type("MockGameMode", (), {"weather": "clear"})()
    def get_nearby_entities(self, entity, radius):
        return {"boosters": self.boosters, "hazards": self.arena.hazards, "balls": self.balls}

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0
        self.active = True

class MockBall:
    def __init__(self, x, y, cosmetic=""):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 15.0
        self.inventory = []
        self.speed = 100.0
        self.base_speed = 100.0
        self.cosmetic = cosmetic
        self.team = 1
        self.ball_type = "normal"
        self.hp = 100
        self.max_hp = 100

def test_snow_boots_pickup():
    from ai.action import Action
    world = MockWorld()
    ball = MockBall(0, 0)
    world.balls.append(ball)

    snow_boots_booster = MockBooster("snow_boots", 0, 0)
    snow_boots_booster.active = True
    world.boosters.append(snow_boots_booster)

    action = Action(ball, world)

    action._collect_booster(1.0)

    assert "snow_boots" in ball.inventory
    assert getattr(ball, "snow_boots_timer", 0.0) == 15.0
    assert snow_boots_booster not in world.boosters

def test_snow_boots_immunity():
    from ai.action import Action
    world = MockWorld()
    ball = MockBall(0, 0)
    ball.inventory = ["snow_boots"]
    world.balls.append(ball)

    world.arena.is_snowing = True

    action = Action(ball, world)

    # Pre-calculate what happens in _apply_weather (which is internal)
    # Actually just call _apply_weather to test if speed gets halved
    # we need to simulate weather loop
    action.execute("idle", 1.0)

    # Speed should not be reduced by snow
    assert ball.base_speed == 100.0

    # Test ice
    ball.vx = 50
    world.arena.is_snowing = False
    world.arena.is_ice = True
    action.execute("idle", 1.0)

    assert getattr(ball, "is_frictionless", False) == False
