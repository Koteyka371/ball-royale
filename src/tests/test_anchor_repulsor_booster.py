import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.projectiles = []
        self.balls = []

class MockBall:
    def __init__(self, id, x, y, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.ball_type = "player"
        self.radius = 10.0
        self.intangible = False
        self.inventory = []
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0

class MockProjectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.radius = 5.0

def test_anchor_repulsor_booster():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)
    world.balls.append(ball)

    booster = MockHazard(105.0, 100.0, "anchor_repulsor_booster")
    booster.active = True
    world.boosters.append(booster)

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._collect_booster(0.016)

    assert getattr(ball, "anchor_repulsor_timer", 0.0) == 10.0
    assert getattr(ball, "anchor_booster_timer", 0.0) >= 10.0
    assert len(world.boosters) == 0

    hazard = MockHazard(110.0, 100.0, "fire")
    world.arena.hazards.append(hazard)

    enemy = MockBall(2, 90.0, 100.0, team="blue")
    world.balls.append(enemy)

    action.execute("idle", 0.1)

    assert ball.anchor_repulsor_timer < 10.0

    # Hazard should be pushed away (x > 110)
    assert hazard.x > 110.0

    # Enemy's velocity should be pushed away (vx < 0)
    assert enemy.vx < 0.0
