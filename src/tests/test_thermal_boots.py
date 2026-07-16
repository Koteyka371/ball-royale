import pytest

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.damage = 0.0

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0

class MockBall:
    def __init__(self, x=0, y=0, radius=10):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.cosmetic = ""
        self.base_speed = 100.0
        self.speed = 100.0
        self.inventory = []
        self.alive = True
        self.team = 1
        self.ball_type = "normal"
        self.hp = 100
        self.max_hp = 100

def test_thermal_boots_pickup():
    from ai.action import Action
    world = MockWorld()
    ball = MockBall(0, 0)
    world.balls.append(ball)

    thermal_boots_booster = MockBooster("thermal_boots", 0, 0)
    thermal_boots_booster.active = True
    world.boosters.append(thermal_boots_booster)

    action = Action(ball, world)

    action._collect_booster(1.0)

    assert "thermal_boots" in ball.inventory
    assert getattr(ball, "thermal_boots_timer", 0.0) == 15.0
    assert thermal_boots_booster not in world.boosters

def test_thermal_boots_immunity():
    from ai.action import Action
    world = MockWorld()
    ball = MockBall(0, 0)
    ball.inventory = ["thermal_boots"]
    world.balls.append(ball)

    ice_patch = MockHazard("ice_patch", 0, 0, 50.0)
    world.arena.hazards.append(ice_patch)

    action = Action(ball, world)

    action.execute("flee", 1.0)

    assert not getattr(ball, "is_frictionless", False)
    assert getattr(ball, "is_slipping", False) == False
    assert ball.speed == 100.0
