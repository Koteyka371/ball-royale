import pytest
from ai.action import Action
from ai.game_modes import CursedBoosterMode

class DummyMode:
    def __init__(self, name):
        self.name = name

class DummyWorld:
    def __init__(self, mode_name=None):
        if mode_name:
            self.mode = DummyMode(mode_name)
        self.boosters = []
        self.arena = DummyArena()

    def _collect_booster(self, ball, booster):
        # Default behavior is to heal, speed up, etc.
        if getattr(booster, "kind", "") == "hp_booster":
            ball.hp = getattr(ball, "hp", 100.0) + 20.0
        elif getattr(booster, "kind", "") == "speed_booster":
            ball.speed = getattr(ball, "speed", 100.0) + 15.0

class DummyArena:
    def __init__(self):
        self.hazards = []

class DummyBall:
    def __init__(self):
        self.id = 1
        self.x = 0
        self.y = 0
        self.radius = 10
        self.hp = 100.0
        self.speed = 100.0
        self.damage = 10.0
        self.stamina = 100.0
        self.ball_type = "normal"
        self.intangible = False
        self.intangible_timer = 0.0

class DummyBooster:
    def __init__(self, kind):
        self.x = 0
        self.y = 0
        self.kind = kind

def test_normal_booster_collection():
    w = DummyWorld()
    b = DummyBall()
    w.boosters.append(DummyBooster("hp_booster"))
    a = Action(b, w)
    a._get_boosters = lambda: w.boosters
    a._get_enemies = lambda: []
    a._collect_booster(0.016)

    assert b.hp == 120.0 # Healed normally

def test_cursed_booster_collection():
    w = DummyWorld("Cursed Boosters")
    b = DummyBall()
    w.boosters.append(DummyBooster("hp_booster"))
    a = Action(b, w)
    a._get_boosters = lambda: w.boosters
    a._get_enemies = lambda: []
    a._collect_booster(0.016)

    # Pre was 100, post is 120, diff is 20.
    # Cursed inverses the diff, so hp should be 100 - 20 = 80
    assert b.hp == 80.0

def test_cursed_speed_collection():
    w = DummyWorld("Cursed Boosters")
    b = DummyBall()
    w.boosters.append(DummyBooster("speed_booster"))
    a = Action(b, w)
    a._get_boosters = lambda: w.boosters
    a._get_enemies = lambda: []
    a._collect_booster(0.016)

    # Pre was 100, post is 115, diff is 15.
    # Cursed inverses the diff, so speed should be 100 - 15 = 85
    assert b.speed == 85.0
    assert getattr(b, "slow_timer", 0.0) == 5.0
