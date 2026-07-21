import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 10000
        self.height = 10000
    def clamp_position(self, x, y, r=0):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.boosters = []
        self.balls = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 300.0
        self.vy = 0.0
        self.radius = 10
        self.hp = 100
        self.alive = True
        self.team = "test"
        self.ball_type = "normal"
        self.max_speed = 10000000
        self.speed = 200
        self.speed = 200
        self.inventory = []

class Hazard:
    def __init__(self, id, x, y, radius, kind, damage=0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.lifetime = 10.0

def test_gravity_multiplier_pickup():
    world = MockWorld()
    ball = MockBall(1, 500, 500)
    world.balls.append(ball)

    booster = Hazard(2, 500, 500, 20, "gravity_multiplier_booster")
    booster.active = True
    world.boosters.append(booster)

    a = Action(ball, world)
    a.execute("collect_booster", 0.016)

    assert getattr(ball, "gravity_multiplier_timer", 0) > 0
    assert len(world.boosters) == 0

def test_gravity_multiplier_effect():
    # Setup without multiplier
    world1 = MockWorld()
    bh1 = Hazard(1, 500, 500, 100, "massive_black_hole", 20.0)
    world1.arena.hazards.append(bh1)
    ball1 = MockBall(1, 200, 400)
    world1.balls.append(ball1)

    a1 = Action(ball1, world1)
    a1.execute("idle", 0.016)

    speed1 = math.hypot(ball1.vx, ball1.vy)

    # Setup with multiplier
    world2 = MockWorld()
    bh2 = Hazard(2, 500, 500, 100, "massive_black_hole", 20.0)
    world2.arena.hazards.append(bh2)
    ball2 = MockBall(2, 200, 400)
    ball2.gravity_multiplier_timer = 10.0
    world2.balls.append(ball2)

    a2 = Action(ball2, world2)
    a2.execute("idle", 0.016)

    speed2 = math.hypot(ball2.vx, ball2.vy)

    assert abs(ball2.x - ball1.x) > 1.0 or abs(ball2.y - ball1.y) > 1.0 or abs(ball2.vx - ball1.vx) > 10.0
