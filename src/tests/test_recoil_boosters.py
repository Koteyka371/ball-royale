import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.items = []
        self.balls = []
        self.leaderboard_manager = type('Mock', (), {'data': {'current_season': 4}})()

    def get_nearby_entities(self, entity, radius):
        return {'items': self.items, 'enemies': [], 'allies': [], 'boosters': self.boosters}

class MockBall:
    def __init__(self, x=0, y=0, ball_id="test"):
        self.id = ball_id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self._base_speed_set = True
        self.recoil_amplifier_timer = 0.0
        self.recoil_dampener_timer = 0.0
        self.vx = 0.0
        self.vy = 0.0

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 5.0

def test_recoil_amplifier_booster():
    ball = MockBall()
    world = MockWorld()
    booster = MockBooster("recoil_amplifier_booster")
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.016)

    assert ball.recoil_amplifier_timer == 10.0
    assert ball.recoil_dampener_timer == 0.0

    target = MockBall(100, 0, "target")
    ball.weapon_type = "ranged"
    action._attempt_damage_internal(ball, target)
    assert ball.vx == -200.0

def test_recoil_dampener_booster():
    ball = MockBall()
    world = MockWorld()
    booster = MockBooster("recoil_dampener_booster")
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.016)

    assert ball.recoil_dampener_timer == 10.0
    assert ball.recoil_amplifier_timer == 0.0

    target = MockBall(100, 0, "target")
    ball.weapon_type = "ranged"
    action._attempt_damage_internal(ball, target)
    assert ball.vx == -20.0
