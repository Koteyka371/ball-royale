import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.safe_zone_center = (500.0, 500.0)
        self.safe_zone_radius = 200.0
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []
        self.next_id = 9000

    def get_nearby_entities(self, ball, radius):
        return {"allies": [], "boosters": self.boosters, "enemies": []}

    def _deal_damage(self, attacker, target):
        damage = getattr(attacker, "damage", 10.0)
        target.hp -= damage

class MockBall:
    def __init__(self, id, team="red", ball_type="warrior", x=10.0, y=10.0, hp=100.0, max_hp=100.0):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.immunity_timer = 0.0

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.x = 15.0
        self.y = 15.0
        self.active = True

def test_teleport_booster_collection():
    world = MockWorld()
    b = MockBall(id=1, x=10.0, y=10.0)
    world.balls.append(b)
    booster = MockBooster("teleport_booster")
    world.boosters.append(booster)

    action = Action(b, world)
    action._collect_booster(1.0) # Move slightly

    # Check if booster was consumed
    assert len(world.boosters) == 0

    # Check if we teleported
    assert b.x != 10.0 or b.y != 10.0

    # Check if we are inside the safe zone radius (plus some buffer, center is 500,500, radius is 200, so dist <= 200)
    dist_to_center = ((b.x - 500.0)**2 + (b.y - 500.0)**2)**0.5
    assert dist_to_center <= 200.0

    # Check if immunity was granted
    assert b.immunity_timer >= 3.0

    # Check if a decoy was spawned
    assert len(world.balls) == 2
    decoy = world.balls[1]
    assert decoy.id != 1
    assert decoy.is_decoy == True
    assert getattr(decoy, "decoy_type", "") == "explosive"
    assert decoy.owner_id == 1
    # Important: Ensure decoy is left at original location
    assert decoy.x == 10.0
    assert decoy.y == 10.0
