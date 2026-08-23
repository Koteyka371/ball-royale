import pytest
import math
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/ai')))

from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []
        self.width = 1000
        self.height = 1000

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

    def get(self, key, default):
        return getattr(self, key, default)

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.boosters = boosters if boosters is not None else []

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b != entity]}

class MockBall:
    def __init__(self, id, x, y, skill, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.skill = skill
        self.active_skill = skill
        self.skill_timer = 0.0
        self.skill_cooldown = 4.0
        self.silence_timer = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "normal"
        self.team = team
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0

def test_fire_sticky_bomb_booster_collection():
    arena = MockArena()
    ball = MockBall(1, 100, 100, "none", team="A")
    booster = MockBooster(100, 100, "fire_sticky_bomb_booster")
    world = MockWorld(arena, [ball], [booster])

    action = Action(ball, world)

    def _get_nearby_entities(entity, radius):
        return {'boosters': world.boosters, 'enemies': []}
    world.get_nearby_entities = _get_nearby_entities

    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.1)

    assert booster not in world.boosters
    assert ball.active_skill == "fire_sticky_bomb"
    assert ball.skill_timer == 4.0
