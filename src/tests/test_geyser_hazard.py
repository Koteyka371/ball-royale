import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, x=0, y=0, radius=40, kind="geyser", active=True, damage=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.active = active
        self.damage = damage
        self.owner_id = -1
        self.duration = 10.0

class MockBall:
    def __init__(self, x=0, y=0, element="", hp=100.0, max_hp=100.0):
        self.id = 1
        self.x = x
        self.y = y
        self.element = element
        self.hp = hp
        self.max_hp = max_hp
        self.speed_multiplier = 1.0
        self.speed_boost_timer = 0.0
        self.fly_timer = 0.0
        self.stun_timer = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.team = "blue"

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": [], "items": []}

def test_geyser_default_effect():
    world = MockWorld()
    ball = MockBall(x=10, y=10)
    world.balls.append(ball)

    hazard = MockHazard(x=10, y=10)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.hp < 100.0
    assert ball.fly_timer >= 2.0
    assert ball.stun_timer >= 1.0
    assert abs(ball.vx) > 0 or abs(ball.vy) > 0

def test_geyser_water_effect():
    world = MockWorld()
    ball = MockBall(x=10, y=10, element="water")
    world.balls.append(ball)

    hazard = MockHazard(x=10, y=10)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.hp == 100.0
    assert ball.speed_multiplier == 1.5
    assert ball.speed_boost_timer >= 2.0
    assert ball.fly_timer == 0.0
    assert ball.stun_timer == 0.0

def test_geyser_earth_effect():
    world = MockWorld()
    ball = MockBall(x=10, y=10, element="earth", hp=50.0)
    world.balls.append(ball)

    hazard = MockHazard(x=10, y=10)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.hp > 50.0
    assert ball.fly_timer == 0.0
    assert ball.stun_timer == 0.0

def test_geyser_inactive_effect():
    world = MockWorld()
    ball = MockBall(x=10, y=10)
    world.balls.append(ball)

    hazard = MockHazard(x=10, y=10, active=False)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.hp == 100.0
    assert ball.fly_timer == 0.0
    assert ball.stun_timer == 0.0
    pass # ball.vx may change due to other logic, just ensure no hp/fly/stun effects
    pass
