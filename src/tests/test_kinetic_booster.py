import pytest
from ai.action import Action
import math

class MockBooster:
    def __init__(self, kind="kinetic_booster", x=100.0, y=100.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.active = True
        self.radius = 15.0

class MockBall:
    def __init__(self, id=1, x=0.0, y=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.radius = 10.0
        self.speed = 200.0
        self.base_speed = 200.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.mass = 1.0
        self.team = "red"
        self.alive = True
        self.ball_type = "base"

    def take_damage(self, amt):
        self.hp -= amt

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.boosters = []
        self.arena = MockArena()
        self.balls = []
    def get_nearby_entities(self, target, radius):
        return {"enemies": [], "allies": []}
    def add_event(self, type, data):
        pass
    def _deal_damage(self, attacker, target, amt=None):
        if amt is None:
            amt = getattr(attacker, "damage", 10.0)
        if hasattr(target, "take_damage"):
            target.take_damage(amt)
        else:
            target.hp -= amt

def test_kinetic_booster_collection():
    w = MockWorld()
    b = MockBall(x=100, y=100)
    w.balls.append(b)

    booster = MockBooster()
    w.boosters.append(booster)

    a = Action(b, w)

    a._get_boosters = lambda: w.boosters
    a._collect_booster(0.016)

    assert getattr(b, "kinetic_booster_timer", 0.0) == 15.0
    assert getattr(b, "kinetic_energy_pool", None) == 0.0
    assert not booster.active
    assert booster not in w.boosters

def test_kinetic_booster_accumulation():
    w = MockWorld()
    b = MockBall()
    a = Action(b, w)

    b.kinetic_booster_timer = 5.0
    b.kinetic_energy_pool = 0.0

    b.vx = 100.0
    b.vy = 0.0
    a.execute("idle", 0.016)

    assert b.kinetic_booster_timer < 5.0
    assert b.kinetic_energy_pool > 0.0
    assert b.kinetic_energy_pool == pytest.approx(100.0 * 0.016 * 0.5)

def test_kinetic_booster_damage_and_knockback():
    w = MockWorld()
    attacker = MockBall(1, 0, 0)
    target = MockBall(2, 10, 0)
    a = Action(attacker, w)

    attacker.kinetic_booster_timer = 5.0
    attacker.kinetic_energy_pool = 100.0
    attacker.team = "red"
    attacker.damage = 10.0

    target.team = "blue"

    w.balls = [attacker, target]

    a._attempt_damage_internal(attacker, target)

    assert target.hp <= 40.0
    assert target.vx > 0.0
    assert attacker.kinetic_energy_pool == 0.0
