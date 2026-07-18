import pytest
from ai.ball_types_alchemist import Alchemist
from ai.action import Action
import math

class MockHazard:
    def __init__(self, kind, x, y, radius, damage):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.platforms = []
        self.is_foggy = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

    def get_nearby_entities(self, target, radius):
        return {"allies": [], "enemies": []}

class MockEnemy:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.radius = 10
        self.ball_type = "basic"
        self.alive = True

def test_alchemist_initialization():
    b = Alchemist(1, 0.0, 0.0)
    assert b.BALL_TYPE == "alchemist"
    assert b.SKILL == "poison_nova"
    assert not hasattr(b, 'speed_multiplier') or getattr(b, 'speed_multiplier', 1.0) == 1.0

def test_alchemist_attack_with_poison():
    b = Alchemist(1, 0.0, 0.0)
    b.speed_multiplier = 1.3

    class Target:
        x, y = 100.0, 0.0
        radius = 10

    target = Target()

    prev_x = b.x
    b.attack(0.1, target)
    assert b.x > prev_x # Alchemist should move

    b.take_damage(10)
    assert b.hp == 80
    assert b.get_hp_percent() == 80.0 / 90.0

def test_alchemist_immunity_and_speed():
    w = MockWorld()
    h = MockHazard("poison_cloud", 0.0, 0.0, 50.0, 10.0)
    w.arena.hazards.append(h)

    b = Alchemist(1, 0.0, 0.0)
    b.speed_multiplier = 1.0 # default
    w.balls.append(b)

    action = Action(b, w)

    # We call execute to see if it sets speed
    action.execute("idle", 0.1)

    assert getattr(b, "speed_multiplier", 1.0) == 1.3
    assert getattr(b, "dot_duration", 0) == 0 # no dot damage should be applied
    assert getattr(b, "dot_damage_per_tick", 0) == 0
    assert b.hp == 90 # immune to direct hazard damage from poison

def test_alchemist_apply_poison_on_attack():
    import random
    random.seed(1)
    w = MockWorld()
    b = Alchemist(1, 0.0, 0.0)
    w.balls.append(b)

    e = MockEnemy()
    w.balls.append(e)

    action = Action(b, w)

    # Force attempt damage many times to trigger 25% probability
    for _ in range(20):
        action._attempt_damage(b, e)

    assert getattr(e, "poison_timer", 0) > 0 or getattr(e, "dot_duration", 0) > 0
