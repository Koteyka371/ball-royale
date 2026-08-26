import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []
        self.balls = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.speed = 100.0
        self.damage = 10.0
        self.hp = 100.0
        self.base_damage = 10.0
        self.base_speed = 100.0
        self.max_hp = 100.0
        self.inventory = []
        self.traits = []

def test_void_artifact_set():
    world = MockWorld()
    ball = MockBall()
    ball.inventory = ["void_shard", "miniature_black_hole"]
    world.balls.append(ball)
    action = Action(ball, world)

    action.execute("idle", 0.1)

    assert abs(ball.speed - 120.0) < 0.1
    assert abs(ball.damage - 12.0) < 0.1

def test_cybernetic_artifact_set():
    world = MockWorld()
    ball = MockBall()
    ball.inventory = ["overclock_booster", "emp_wave_item"]
    world.balls.append(ball)
    action = Action(ball, world)

    action.execute("idle", 0.1)

    assert abs(ball.speed - 130.0) < 0.1
    assert abs(ball.damage - 10.0) < 0.1

def test_blood_artifact_set():
    world = MockWorld()
    ball = MockBall()
    ball.has_blood_pact_artifact = True
    ball.inventory = ["blood_orb"]
    world.balls.append(ball)
    action = Action(ball, world)

    action.execute("idle", 0.1)

    # Blood Pact alone doubles speed and damage, we expect it to stack with 1.3x damage set bonus.
    # But wait, blood pact applies its own multiplier independently later in execute().
    # It does: self.ball.speed = base_speed_blood_pact * 2.0 (which will overwrite the set bonus speed if it wasn't there).
    # Since set bonus affects base_damage and blood pact affects damage directly (or sets base_damage_blood_pact on first tick),
    # on first tick it sets base_damage_blood_pact to 13.0, then sets damage to 26.0.

    assert abs(ball.speed - 200.0) < 0.1
    assert abs(ball.damage - 26.0) < 0.1

def test_no_artifact_set():
    world = MockWorld()
    ball = MockBall()
    ball.inventory = ["void_shard"]
    world.balls.append(ball)
    action = Action(ball, world)

    action.execute("idle", 0.1)

    assert abs(ball.speed - 100.0) < 0.1
    assert abs(ball.damage - 10.0) < 0.1
