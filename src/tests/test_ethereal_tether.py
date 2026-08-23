import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, team=1, id="ball_1"):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = "player"
        self.id = id
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.speed = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.perception_radius = 5000.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.items = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters, "hazards": self.arena.hazards, "enemies": [], "allies": [b for b in self.balls if b != ball]}

def test_ethereal_tether_booster_collection():
    w = MockWorld()
    b1 = MockBall(0, 0, 1, "b1")
    b2 = MockBall(10, 10, 1, "b2")
    w.balls = [b1, b2]

    class Booster:
        kind = "ethereal_tether_booster"
        active = True
        x = 5
        y = 5

    booster = Booster()
    w.boosters.append(booster)

    action = Action(b1, w)

    # Run a tick to collect booster
    action.execute("opportunistic", 0.1)

    print(f"b1 attrs: {b1.__dict__}")
    assert getattr(b1, "ethereal_tether_timer", 0) > 0
    assert getattr(b2, "ethereal_tether_timer", 0) > 0
    assert len(getattr(b1, "ethereal_tether_links", [])) == 1
    assert b1.ethereal_tether_links[0] == b2
    assert b2.ethereal_tether_links[0] == b1
    assert booster.active == False
    assert booster not in w.boosters

def test_ethereal_tether_damage_and_healing_sharing():
    w = MockWorld()
    b1 = MockBall(0, 0, 1, "b1")
    b2 = MockBall(10, 10, 1, "b2")
    w.balls = [b1, b2]

    b1.ethereal_tether_timer = 10.0
    b1.ethereal_tether_links = [b2]
    b2.ethereal_tether_timer = 10.0
    b2.ethereal_tether_links = [b1]

    action = Action(b1, w)
    b1._mock_damage_taken = 20.0

    action.execute("opportunistic", 0.1)

    # 20 damage shared by 2 = 10 each
    assert b1.hp == 90.0
    assert b2.hp == 90.0

    # Healing sharing
    b1._mock_damage_taken = -10.0  # Means 10 healing
    action.execute("opportunistic", 0.1)

    # 10 healing shared by 2 = 5 each
    assert b1.hp == 95.0
    assert b2.hp == 95.0

def test_ethereal_tether_teleport():
    w = MockWorld()
    b1 = MockBall(0, 0, 1, "b1")
    b2 = MockBall(100, 100, 1, "b2")
    w.balls = [b1, b2]

    b1.ethereal_tether_timer = 10.0
    b1.ethereal_tether_links = [b2]
    b1.ethereal_tether_teleport_charges = 1
    b2.ethereal_tether_timer = 10.0
    b2.ethereal_tether_links = [b1]
    b2.ethereal_tether_teleport_charges = 1

    action = Action(b1, w)

    # b1 drops below 20%
    b1._mock_damage_taken = 90.0 # From 100 HP. Shares 90/2 = 45. B1 is left with 100-45 = 55. Not below 20%.

    # Let's set b1 hp to 50, take 80 damage. 80/2 = 40. B1 hp = 10.
    b1.hp = 50.0
    b2.hp = 100.0

    b1._mock_damage_taken = 80.0

    action.execute("opportunistic", 0.1)

    # 80 damage shared -> 40 each.
    # b1 new hp = 10.0 (which is <= 20% of 100 max_hp)
    # b2 new hp = 60.0

    # b1 should teleport to b2 (x=100, y=100)
    assert b1.hp == 10.0
    assert b2.hp == 60.0
    assert abs(b1.x - 100.0) < 20.0
    assert abs(b1.y - 100.0) < 20.0
    assert getattr(b1, "ethereal_tether_teleport_charges", 1) == 0
