import pytest
from ai.action import Action
from ai.ball_types_decoy_master import DecoyMaster

class MockBall:
    def __init__(self, x=0, y=0, team=1, id=1, ball_type="decoy_master"):
        self.x = x
        self.y = y
        self.team = team
        self.id = id
        self.ball_type = ball_type
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.speed = 2.0
        self.radius = 10.0
        self.personality = "defender"

class MockDecoy:
    def __init__(self, x, y, owner_id):
        self.x = x
        self.y = y
        self.is_decoy = True
        self.alive = True
        self.owner_id = owner_id
        self.team = 1

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls or []
        self.events = []

    def _deal_damage(self, attacker, defender, amount=None):
        pass

def test_decoy_master_shield():
    dm = MockBall(x=0, y=0, ball_type="decoy_master", id=99)
    d1 = MockDecoy(x=10, y=10, owner_id=99)
    d2 = MockDecoy(x=20, y=20, owner_id=99)
    d3 = MockDecoy(x=1000, y=1000, owner_id=99) # Too far

    world = MockWorld([dm, d1, d2, d3])

    action = Action(dm, world)
    action.execute("defend", 1.0)

    assert getattr(dm, "energy_shield_active", False) == True
    assert dm.energy_shield_hp == 30.0 # 2 near decoys * 15
