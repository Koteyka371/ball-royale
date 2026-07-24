import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = type("Arena", (), {"hazards": []})
        self.balls = []
        self.events = []
        self.boosters = []

    def _deal_damage(self, attacker, defender, amount=None):
        dmg = amount if amount is not None else getattr(attacker, "damage", 10.0)
        defender.hp -= dmg
        if defender.hp <= 0:
            defender.alive = False

class MockBall:
    def __init__(self, x, y, id, team="A"):
        self.x = x
        self.y = y
        self.id = id
        self.hp = 150
        self.alive = True
        self.radius = 10
        self.team = team
        self.ball_type = "normal"
        self.vx = 0
        self.vy = 0
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 20
        self.duration = 0.0
        self.attached_id = None
        self.owner_id = None
        self.trap_variant = ""

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

def test_parasite_attaches():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    parasite = MockHazard(10, 0, "lightning_parasite_trap")
    world.arena.hazards.append(parasite)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert parasite.attached_id == 1
    assert parasite.duration == 9999.0

def test_parasite_damages_teammates():
    world = MockWorld()
    b1 = MockBall(0, 0, 1, team="A")
    b2 = MockBall(50, 0, 2, team="A") # Nearby teammate
    world.balls.extend([b1, b2])

    parasite = MockHazard(0, 0, "lightning_parasite_trap")
    parasite.attached_id = 1
    parasite.parasite_hp = 50.0
    parasite.tick_timer = 0.0
    world.arena.hazards.append(parasite)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert b2.hp == 140 # 150 - 10
    assert parasite.tick_timer > 0

def test_parasite_dies_on_damage():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    parasite = MockHazard(0, 0, "lightning_parasite_trap")
    parasite.attached_id = 1
    parasite.parasite_hp = 50.0
    parasite.last_hp = 150.0
    world.arena.hazards.append(parasite)

    # Ball takes damage
    b1.hp = 90.0

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert getattr(parasite, "parasite_hp", 0) <= 0
    assert parasite.duration == 0.0

def test_parasite_cleansed():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    parasite = MockHazard(0, 0, "lightning_parasite_trap")
    parasite.attached_id = 1
    parasite.duration = 9999.0
    world.arena.hazards.append(parasite)

    cleanser = MockBooster(0, 0, "cleanser")
    world.boosters.append(cleanser)

    action = Action(b1, world)
    # The action will collect the booster because it's idle and near
    action._get_boosters = lambda: [cleanser]
    action._get_enemies = lambda: []
    action._collect_booster(0.1)

    assert parasite.duration == 0.0
