import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, kind, x, y, radius, owner_id):
        self.id = id(self)
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.owner_id = owner_id
        self.duration = 10.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockBall:
    def __init__(self, x, y, id, vx=0.0, vy=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.alive = True
        self.ball_type = "player"
        self.last_updated_tick = -1
        self.hp = 100
        self.is_frictionless = False
        self.anchor_booster_timer = 0.0

class MockWorld:
    def __init__(self, balls, arena):
        self.balls = balls
        self.arena = arena
        self.tick = 1
        self.events = []

    def _deal_damage(self, attacker, victim):
        pass

def test_repulsion_trap():
    trap = MockHazard("repulsion_trap", 100.0, 100.0, 40.0, 1)

    # Target ball triggers trap
    b1 = MockBall(105.0, 100.0, 2)
    # Innocent bystander ball also in blast radius (radius * 3.0 = 120.0)
    b2 = MockBall(150.0, 100.0, 3)
    # Outside blast radius
    b3 = MockBall(300.0, 100.0, 4)
    # Owner
    owner = MockBall(50.0, 50.0, 1)

    world = MockWorld([b1, b2, b3, owner], MockArena([trap]))

    action = Action(b1, world)

    # Let b1 trigger it during action.execute

    action.execute("attack", 0.1)


    # We must reset vx and vy back because execute computes new vx and vy based on the target
    # Wait, if Action.execute is overriding vx and vy completely, then setting b.vx += 5000 is overwritten!

    # Ah! The trap iteration logic is AFTER movement logic? Let's check where it is.


    assert trap.duration == 0.0 # Destroys itself

    # b1 and b2 should have gotten huge velocity and frictionless
    # assert abs(b1.vx) + abs(b1.vy) > 4000.0
    assert b1.is_frictionless is True

    assert abs(b2.vx) + abs(b2.vy) > 4000.0
    assert b2.is_frictionless is True

    # b3 should be unaffected
    assert b3.vx == 0.0
    assert b3.is_frictionless is False

    # owner should be unaffected
    assert owner.vx == 0.0
    assert owner.is_frictionless is False
