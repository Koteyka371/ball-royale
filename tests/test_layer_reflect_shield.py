from unittest.mock import MagicMock
from src.ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.boosters = []
        self.arena = MagicMock()
        self.arena.hazards = []

    def _deal_damage(self, attacker, target):
        if hasattr(target, "take_damage"):
            target.take_damage(attacker.damage)

class MockBall:
    def __init__(self, id, x, y, radius=10.0, damage=10.0, hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.hp = hp
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "test"

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10.0
        self.active = True

def test_layer_reflect_booster_pickup():
    world = MockWorld()
    b1 = MockBall(1, 0, 0)

    booster = MockBooster(0, 0, "layer_reflect_shield_booster")
    world.boosters.append(booster)

    action = Action(b1, world)
    action._collect_booster(0.1)

    assert getattr(b1, "reflect_shield_active", False) == True
    assert getattr(b1, "reflect_shield_max_layers", 1) == 3
    assert getattr(b1, "reflect_shield_current_layers", 1) == 3
