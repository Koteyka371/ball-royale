import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/ai')))

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
        self.hp = 150
        self.alive = True
        self.radius = 10
        self.team = id
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

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

    def get(self, key, default):
        return getattr(self, key, default)

def test_sticky_bomb_trap_attaches():
    world = MockWorld()
    world.next_id = 9999
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    bomb = MockHazard(10, 0, "sticky_bomb_trap")
    world.arena.hazards.append(bomb)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert bomb.attached_id == 1
    assert bomb.duration == 3.0 or bomb.duration == 2.9

    b1.x = 50
    b1.y = 50
    action.execute("idle", 0.1)

    assert bomb.x == 50
    assert bomb.y == 50

def test_sticky_bomb_trap_transfers():
    world = MockWorld()
    world.next_id = 9999
    b1 = MockBall(0, 0, 1)
    b2 = MockBall(100, 100, 2)
    world.balls.extend([b1, b2])

    bomb = MockHazard(10, 0, "sticky_bomb_trap")
    world.arena.hazards.append(bomb)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert bomb.attached_id == 1
    bomb.duration = 1.0

    # b2 comes close
    b2.x = 10
    b2.y = 0
    action.execute("idle", 0.1)

    assert bomb.attached_id == 2
    assert bomb.duration == 3.0 or bomb.duration == 2.9

def test_sticky_bomb_trap_explodes():
    world = MockWorld()
    world.next_id = 9999
    b1 = MockBall(0, 0, 1)
    world.balls.append(b1)

    bomb = MockHazard(0, 0, "sticky_bomb_trap")
    bomb.attached_id = 1
    bomb.duration = 0.05
    world.arena.hazards.append(bomb)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert b1.hp == 50 # 150 - 100
    assert bomb not in world.arena.hazards
