import pytest
from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = id(self)
        self.x = 100
        self.y = 100
        self.radius = 10.0
        self.is_blinded = False
        self.perception_radius = 250.0
        self.alive = True
        self.speed = 100
        self.base_speed = 100
        self.vx = 0
        self.vy = 0
        self.team = "player"
        self.ball_type = "basic"

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.id = id(self)
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.damage = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
    def add_event(self, t, d):
        pass
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}

def test_blindness_zone_applies():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    hazard = MockHazard("blindness_zone", 100, 100, 30.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # Run one tick inside the zone
    action.execute("idle", 0.016)

    assert getattr(ball, "is_blinded", False) == True
    assert getattr(ball, "perception_radius") == 0.0
    assert getattr(ball, "blindness_timer", 0.0) > 0.0
    assert getattr(ball, "base_perception_radius", 0.0) == 250.0

    # Move ball out of zone
    ball.x = 500
    ball.y = 500

    # Run a tick where time passes and clears the timer
    action.execute("idle", 0.3)

    assert getattr(ball, "is_blinded", False) == False
    assert getattr(ball, "perception_radius") == 250.0
