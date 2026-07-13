import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.ai.action import Action

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
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.hp = 100
        self.alive = True
        self.radius = 10
        self.team = id
        self.ball_type = "normal"
        self.vx = 0
        self.vy = 0

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 20
        self.duration = 10.0
        self.attached_id = None
        self.owner_id = None

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

def test_sticky_mine_attaches():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    mine = MockHazard(10, 0, "sticky_mine")
    world.arena.hazards.append(mine)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert mine.attached_id == 1

    b1.x = 50
    b1.y = 50
    action.execute("idle", 0.1)

    assert mine.x == 50
    assert mine.y == 50

def test_sticky_mine_transfers():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    b2 = MockBall(100, 100, 2)
    world.balls.extend([b1, b2])

    mine = MockHazard(10, 0, "sticky_mine")
    world.arena.hazards.append(mine)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert mine.attached_id == 1

    # b2 comes close
    b2.x = 10
    b2.y = 0
    action.execute("idle", 0.1)

    assert mine.attached_id == 2

def test_sticky_mine_explodes():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    mine = MockHazard(0, 0, "sticky_mine")
    mine.duration = 0.05
    world.arena.hazards.append(mine)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert b1.hp == 50
    assert mine not in world.arena.hazards

def test_sticky_mine_booster_collect():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    booster = MockBooster(5, 5, "sticky_mine_booster")
    world.boosters.append(booster)

    action = Action(b1, world)
    action._collect_booster(0.1)

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "sticky_mine"
    assert len(world.boosters) == 0
