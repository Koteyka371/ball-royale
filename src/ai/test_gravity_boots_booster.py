import pytest
import math
from ai.action import Action
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self):
        self.hazards = []
        self.wind_dx = 0.0
        self.wind_dy = 0.0
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 50000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.tick = 0
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": self.boosters, "hazards": self.arena.hazards}

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.speed = 0.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.base_speed = 0.0 # Make it 0 to avoid random idle walking
        self._base_speed_set = True
        self.ball_type = "warrior"
        self.gravity_boots_booster_timer = 0.0
        self.pull_booster_timer = 0.0
        self.gravity_well_aura_timer = 0.0

class MockBooster:
    def __init__(self, kind, x, y):
        self.id = 99
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0
        self.ball_type = "booster"

def test_gravity_boots_booster_pickup():
    world = MockWorld()
    ball = MockBall()
    ball.x = 500.0
    ball.y = 500.0
    world.balls.append(ball)

    booster = MockBooster("gravity_boots_booster", 500.0, 500.0)
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("collect_booster", 0.1)

    assert ball.gravity_boots_booster_timer == 14.9
    assert len(world.boosters) == 0

def test_gravity_boots_booster_pull_reduction():
    # Setup without boots
    world1 = MockWorld()
    ball1 = MockBall()
    world1.balls.append(ball1)

    gw1 = Hazard(id=1, x=200.0, y=100.0, radius=50.0, kind="gravity_well", damage=0.0)
    world1.arena.hazards.append(gw1)

    action1 = Action(ball1, world1)
    action1._idle = lambda d: None
    action1._chase = lambda d: None
    action1._attack = lambda d: None
    action1._process_physics = lambda delta: None

    action1.execute("idle", 1.0)
    dist1 = ball1.x - 100.0

    # Setup with boots
    world2 = MockWorld()
    ball2 = MockBall()
    ball2.gravity_boots_booster_timer = 15.0
    world2.balls.append(ball2)

    gw2 = Hazard(id=2, x=200.0, y=100.0, radius=50.0, kind="gravity_well", damage=0.0)
    world2.arena.hazards.append(gw2)

    action2 = Action(ball2, world2)
    action2._idle = lambda d: None
    action2._chase = lambda d: None
    action2._attack = lambda d: None
    action2._process_physics = lambda delta: None

    action2.execute("idle", 1.0)
    dist2 = ball2.x - 100.0

    assert math.isclose(dist2, dist1 * 0.1, rel_tol=1e-5)
    assert ball2.gravity_boots_booster_timer == 14.0
