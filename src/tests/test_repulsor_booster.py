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

def test_repulsor_booster_collection():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)

    booster = MockHazard(105.0, 100.0, "repulsor_booster")
    booster.active = True
    world.boosters.append(booster)

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._collect_booster(0.016)

    assert getattr(ball, "repulsor_booster_timer", 0.0) == 10.0
    assert len(world.boosters) == 0

def test_repulsor_booster_aura_repels_hazards_and_projectiles():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)
    ball.repulsor_booster_timer = 5.0

    # Place a hazard close to the ball
    hazard = MockHazard(110.0, 100.0, "fire")
    world.arena.hazards.append(hazard)

    # Place a projectile close to the ball
    proj = MockProjectile(90.0, 100.0)
    world.projectiles.append(proj)

    action = Action(ball, world)
    # The execute logic will run the aura if strategy isn't one that skips normal tick,
    # let's just pass "idle" or something.
    action.execute("idle", 0.1)

    assert ball.repulsor_booster_timer < 5.0

    # Hazard should be pushed to the right (x > 110)
    assert hazard.x > 110.0
    # Projectile should be pushed to the left (x < 90)
    assert proj.x < 90.0
