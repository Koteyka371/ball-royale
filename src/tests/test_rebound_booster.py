import pytest

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
    def clamp_position(self, x, y, radius):
        bounced = False
        if x < radius:
            x = radius
            bounced = True
        elif x > self.width - radius:
            x = self.width - radius
            bounced = True
        if y < radius:
            y = radius
            bounced = True
        elif y > self.height - radius:
            y = self.height - radius
            bounced = True
        return x, y, bounced

class MockGameMode:
    pass

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockWorld:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.arena = MockArena()
        self.game_mode = MockGameMode()
        self.balls = []
        self.boosters = []

class MockBall:
    def __init__(self, x=500, y=500):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.radius = 10.0
        self.alive = True
        self.intangible = False

from ai.action import Action

def test_rebound_booster_pickup():
    ball = MockBall(500, 500)
    w = MockWorld()
    w.balls = [ball]
    booster = MockBooster(500, 500, "rebound_booster")
    w.boosters.append(booster)
    a = Action(ball, w)

    a._get_boosters = lambda: w.boosters
    a._collect_booster(0.016)

    assert getattr(ball, "rebound_booster_timer", 0) > 0
    assert len(w.boosters) == 0

def test_rebound_booster_bounce():
    ball = MockBall(5, 500) # Out of bounds to force a clamp and bounce
    ball.rebound_booster_timer = 5.0

    w = MockWorld()
    w.balls = [ball]
    a = Action(ball, w)

    bounced = a._clamp_position()
    assert bounced is True

    assert getattr(ball, "speed_boost_timer", 0) == 2.0
    assert getattr(ball, "energy_shield_timer", 0) == 2.0

def test_rebound_booster_tick():
    ball = MockBall(500, 500)
    ball.rebound_booster_timer = 5.0

    w = MockWorld()
    w.balls = [ball]
    a = Action(ball, w)

    a.execute("idle", 1.0)

    assert ball.rebound_booster_timer == 4.0
