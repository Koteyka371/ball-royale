import pytest
import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.alive = True
        self.speed = 100.0
        self.leech_booster_timer = 0.0
        self.leech_seed_timer = 0.0
        self.leech_seed_attacker_id = None
        self.ball_type = "test"
        self.status_effects = []
        self.inventory = []
        self.combo_count = 0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []

    def _deal_damage(self, attacker, target):
        target.hp -= getattr(attacker, "damage", 10.0)

def test_leech_seed_plant_and_drain():
    attacker = MockBall(1, 100, 100)
    target = MockBall(2, 110, 110)
    world = MockWorld()
    world.balls = [attacker, target]

    # attacker has the booster
    attacker.leech_booster_timer = 10.0

    action_attacker = Action(attacker, world)
    action_target = Action(target, world)

    # Simulate attacker hitting target
    action_attacker._attempt_damage(attacker, target)

    assert target.hp < 100.0 # damage was dealt
    assert target.leech_seed_timer == 5.0
    assert target.leech_seed_attacker_id == attacker.id

    attacker.hp = 50.0 # Set attacker HP to something low

    # Simulate target executing (where drain happens)
    action_target.execute("idle", 1.0)

    # target should take 5 drain damage
    assert target.hp == 90.0 - 5.0
    # attacker should heal 5
    assert attacker.hp == 55.0
