import pytest
from unittest.mock import MagicMock
from ai.action import Action

class MockBall:
    def __init__(self, id, ball_type, x, y):
        self.id = id
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.radius = 10
        self.speed = 0
        self.damage = 20
        self.team = "A"
        self.vx = 0
        self.vy = 0

    def take_damage(self, amount):
        self.hp -= amount

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y

class MockArena:
    def __init__(self):
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 2000
        self.hazards = []
    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [], "allies": [], "hazards": [], "boosters": self.boosters}

    def _deal_damage(self, attacker, target):
        target.take_damage(attacker.damage)

def test_collect_half_reflect_shield():
    world = MockWorld()
    ball = MockBall(1, "test_ball", 0, 0)
    world.balls.append(ball)

    action = Action(ball, world)

    booster = MockBooster("half_reflect_shield_booster", 5, 5)
    world.boosters.append(booster)

    action._collect_booster(0.1)

    assert getattr(ball, "half_reflect_shield_active", False) == True
    assert getattr(ball, "half_reflect_shield_timer", 0.0) == 5.0
    assert len(world.boosters) == 0

def test_half_reflect_shield_timer():
    world = MockWorld()
    ball = MockBall(1, "test_ball", 0, 0)
    ball.half_reflect_shield_active = True
    ball.half_reflect_shield_timer = 5.0

    action = Action(ball, world)
    action.execute("none", 1.0)

    assert ball.half_reflect_shield_timer == 4.0
    assert ball.half_reflect_shield_active == True

    action.execute("none", 4.0)
    assert ball.half_reflect_shield_timer <= 0.0
    assert ball.half_reflect_shield_active == False

def test_half_reflect_shield_damage():
    world = MockWorld()
    target = MockBall(1, "target_ball", 0, 0)
    target.half_reflect_shield_active = True
    target.half_reflect_shield_timer = 5.0

    attacker = MockBall(2, "attacker_ball", 100, 100)
    attacker.damage = 40

    action = Action(target, world)

    action._attempt_damage(attacker, target)

    # Target takes no damage
    assert target.hp == 100
    # Attacker takes 50% damage
    assert attacker.hp == 80

if __name__ == '__main__':
    pytest.main(['-v', __file__])
