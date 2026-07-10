import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = alive
        self.radius = 15.0
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0

class MockHazard:
    def __init__(self, kind, x, y, owner_id):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 40.0
        self.owner_id = owner_id
        self.damage = 5.0
        self.knockback = 5000.0
        self.duration = 10.0
        self.emp_disabled_timer = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

    def _deal_damage(self, attacker, target, dmg=None):
        if dmg is None:
            dmg = attacker.damage
        target.hp -= dmg

def test_mine_bounce():
    world = MockWorld()
    b1 = MockBall(1, 0.0, 0.0) # Will trigger the mine
    b2 = MockBall(2, 50.0, 0.0) # Will get caught in blast radius
    b3 = MockBall(3, 1000.0, 0.0) # Won't get caught
    owner = MockBall(99, -100.0, 0.0) # Owner won't trigger it

    world.balls.extend([b1, b2, b3, owner])

    mine = MockHazard("mine_bounce", 20.0, 0.0, owner.id)
    world.arena.hazards.append(mine)

    action = Action(b1.id, world)
    action.ball = b1

    # Tick simulation
    action.execute("idle", 0.1)

    # Validate b1 knockback and hp
    assert b1.hp == 95.0
    assert abs(b1.vx) > 1.0 # pushed away from mine

    # Validate b2 knockback and hp
    assert b2.hp == 95.0
    assert abs(b2.vx) > 1.0 # pushed away from mine

    # Validate b3 no effect
    assert b3.hp == 100.0
    assert b3.vx == 0

    # Validate hazard destruction
    assert mine.duration == 0.0
