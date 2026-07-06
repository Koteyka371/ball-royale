import pytest
from src.ai.action import Action

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.vx = 100.0
        self.vy = 0.0
        self.radius = 10.0
        self.speed = 2.0
        self.damage_multiplier = 1.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.alive = True
        self.bumper_combo = 0

class MockHazard:
    def __init__(self, kind, powerup_type=None, x=0.0, y=0.0):
        self.kind = kind
        self.powerup_type = powerup_type
        self.x = x
        self.y = y
        self.radius = 20.0
        self.duration = 10.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

    def clamp_position(self, *args):
        return args[0], args[1], False

    def update_zone(self, *args):
        pass

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.balls = []
        self.boosters = []
        self.events = []
        self.dead_balls = []

    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters, "enemies": [], "allies": []}


def test_cursed_bumper_activation():
    ball = MockBall(0.0, 0.0)
    hazard = MockHazard("bumper", "cursed", 0.0, 0.0)

    world = MockWorld(MockArena([hazard]))
    world.balls = [ball]

    action = Action(ball, world)

    action.execute("none", 0.1)

    assert getattr(ball, "cursed_bumper_active", False) is True
    assert getattr(ball, "base_damage_multiplier", 1.0) == 1.0
    assert getattr(ball, "base_speed", 2.0) == 2.0
    assert ball.damage_multiplier == 3.0


def test_cursed_bumper_dot():
    ball = MockBall(0.0, 0.0)
    ball.cursed_bumper_active = True

    world = MockWorld(MockArena([]))
    world.balls = [ball]

    action = Action(ball, world)

    action.execute("none", 1.0)

    # Base hp was 100, dot is 5.0 * 1.0 = 95.0
    assert ball.hp == 95.0


def test_cursed_bumper_cure():
    ball = MockBall(0.0, 0.0)
    ball.cursed_bumper_active = True
    ball.base_damage_multiplier = 1.0
    ball.damage_multiplier = 3.0

    # Hit a normal bumper (e.g., speed bumper)
    hazard = MockHazard("bumper", "speed", 0.0, 0.0)

    world = MockWorld(MockArena([hazard]))
    world.balls = [ball]

    action = Action(ball, world)

    action.execute("none", 0.1)

    assert getattr(ball, "cursed_bumper_active", False) is False
    assert ball.damage_multiplier == 1.0
