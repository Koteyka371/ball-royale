import pytest
from ai.action import Action
import random

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.boosters = arena.hazards

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.stun_timer = 0
        self.radius = 10.0
        self.inventory = []
        self.speed = 10.0
        self.vx = 0
        self.vy = 0

    def take_damage(self, dmg):
        self.hp -= dmg

def test_dummy_item_collection():
    class MockDummyItem:
        def __init__(self, x, y):
            self.kind = "dummy_item"
            self.x = x
            self.y = y
            self.radius = 15.0
            self.damage = 50.0
            self.stun_duration = 2.0
            self.active = True

    arena = MockArena([MockDummyItem(0, 0)])
    enemy = MockBall(2, 5, 0, team="teamB")

    world = MockWorld(arena, [enemy])
    action = Action(enemy, world)

    action.execute("collect_booster", 0.016)

    assert enemy.hp < 100
    assert enemy.stun_timer > 0
