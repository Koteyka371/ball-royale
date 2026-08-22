import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b != entity]}

class MockBall:
    def __init__(self, id, x, y, skill, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.skill = skill
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

def test_fire_sticky_bomb_skill_spawns_hazard():
    arena = MockArena()
    ball = MockBall(1, 100, 100, "fire_sticky_bomb", team="A")
    enemy = MockBall(2, 200, 100, "none", team="B")
    world = MockWorld(arena, [ball, enemy])
    action = Action(ball, world)

    action._use_skill()

    assert len(arena.hazards) == 1
    hazard = arena.hazards[0]
    assert hazard.kind == "thrown_sticky_bomb"
    assert getattr(hazard, "vx", 0.0) > 0.0
    assert getattr(hazard, "vy", 0.0) == 0.0

def test_thrown_sticky_bomb_sticks_to_enemy():
    arena = MockArena()
    ball = MockBall(1, 100, 100, "fire_sticky_bomb", team="A")
    enemy = MockBall(2, 200, 100, "none", team="B")
    world = MockWorld(arena, [ball, enemy])
    action = Action(ball, world)

    # Manually inject the thrown hazard near the enemy
    class TempHazard:
        pass
    hazard = TempHazard()
    hazard.id = 19101
    hazard.x = 190
    hazard.y = 100
    hazard.vx = 100
    hazard.vy = 0
    hazard.radius = 15
    hazard.kind = "thrown_sticky_bomb"
    hazard.duration = 2.0
    hazard.owner_id = 1
    arena.hazards.append(hazard)

    action.execute("idle", 0.1)

    assert hazard.kind == "sticky_bomb"
    assert hazard.vx == 0
    assert hazard.vy == 0
    assert hazard.duration == 3.0
    assert getattr(hazard, "attached_id", None) == 2

def test_thrown_sticky_bomb_sticks_to_wall():
    arena = MockArena()
    ball = MockBall(1, 100, 100, "fire_sticky_bomb", team="A")
    world = MockWorld(arena, [ball])
    action = Action(ball, world)

    # Manually inject hazard near left wall
    class TempHazard:
        pass
    hazard = TempHazard()
    hazard.id = 19102
    hazard.x = 10
    hazard.y = 500
    hazard.vx = -100
    hazard.vy = 0
    hazard.radius = 15
    hazard.kind = "thrown_sticky_bomb"
    hazard.duration = 2.0
    hazard.owner_id = 1
    arena.hazards.append(hazard)

    action.execute("idle", 0.1)

    assert hazard.kind == "sticky_bomb"
    assert hazard.vx == 0
    assert hazard.vy == 0
    assert hazard.duration == 3.0
    assert getattr(hazard, "attached_id", None) is None
