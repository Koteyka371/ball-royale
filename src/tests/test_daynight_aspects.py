import pytest
from ai.action import Action

class MockBall:
    def __init__(self, traits=None, ball_type="normal", hp=50.0, max_hp=100.0):
        self.traits = traits or []
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = max_hp
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.burn_timer = 0.0
        self.invisible_timer = 0.0
        self.slow_timer = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.stamina = 100.0

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0.0
        self.y = 0.0
        self.radius = 15.0
        self.active = True

class MockWorld:
    def __init__(self):
        self.boosters = []
        self.arena = self.MockArena()

    class MockArena:
        def __init__(self):
            self.hazards = []

def test_sun_aspect_light_unit():
    ball = MockBall(traits=["light"])
    booster = MockBooster("sun_aspect")
    world = MockWorld()
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.1)

    assert ball.hp == 80.0
    assert not booster.active
    assert booster not in world.boosters

def test_sun_aspect_shadow_unit():
    ball = MockBall(traits=["shadow"])
    booster = MockBooster("sun_aspect")
    world = MockWorld()
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.1)

    assert ball.burn_timer == 5.0
    assert not booster.active
    assert booster not in world.boosters

def test_moon_aspect_light_unit():
    ball = MockBall(traits=["light"])
    booster = MockBooster("moon_aspect")
    world = MockWorld()
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.1)

    assert ball.slow_timer == 5.0
    assert not booster.active
    assert booster not in world.boosters

def test_moon_aspect_shadow_unit():
    ball = MockBall(traits=["shadow"])
    booster = MockBooster("moon_aspect")
    world = MockWorld()
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.1)

    assert ball.invisible_timer == 5.0
    assert not booster.active
    assert booster not in world.boosters
