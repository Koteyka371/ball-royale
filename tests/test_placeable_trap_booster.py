import pytest
from ai.action import Action
from arena.procedural_arena import Hazard
import math

class MockBooster:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

    def get(self, key, default):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.speed = 100.0
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.inventory = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_placeable_trap_booster_collection():
    ball = MockBall(1, 0, 0)
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    booster = MockBooster('placeable_trap_booster', 5, 5, 10)
    world.boosters.append(booster)

    action._get_enemies = lambda: []
    action._get_boosters = lambda: [booster]

    action._collect_booster(0.1)

    assert "placeable_trap_booster" in ball.inventory
    assert len(world.boosters) == 0

def test_placeable_trap_booster_deploy():
    ball = MockBall(1, 0, 0)
    ball.inventory.append("placeable_trap_booster")
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    action.execute("flee", 0.1)

    assert "placeable_trap_booster" not in ball.inventory
    assert len(world.arena.hazards) == 1

    trap = world.arena.hazards[0]
    assert trap.kind == "pull_trap"
    assert trap.owner_id == ball.id

def test_placeable_trap_booster_effect():
    owner = MockBall(1, 0, 0)
    enemy = MockBall(2, 50, 0)
    world = MockWorld()
    world.balls.extend([owner, enemy])

    trap = Hazard(1, 0, 0, 40.0, "pull_trap", 10.0)
    trap.owner_id = owner.id
    world.arena.hazards.append(trap)

    action = Action(enemy, world)

    # 50 squared is 2500 < 10000, so enemy should be pulled
    old_x = enemy.x
    action._update_skill_timer(0.1)

    assert enemy.x < old_x # Pulled towards 0, 0
    assert enemy.hp < 100.0 # Took damage
