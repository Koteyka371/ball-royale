import pytest
import sys
sys.path.append('src')
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

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

def test_lightning_rod_pickup():
    world = MockWorld()
    ball = MockBall(0, 0)
    world.balls.append(ball)

    lightning_rod_booster = MockBooster("lightning_rod_item", 0, 0)
    lightning_rod_booster.active = True
    world.boosters.append(lightning_rod_booster)

    action = Action(ball, world)
    action._collect_booster(1.0)

    assert getattr(ball, "has_lightning_rod", False)
    assert lightning_rod_booster not in world.boosters
