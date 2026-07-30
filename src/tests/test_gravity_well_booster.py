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

def test_gravity_well_booster_collection():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)

    booster = MockHazard(105.0, 100.0, "gravity_well_booster")
    booster.active = True
    world.boosters.append(booster)

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._collect_booster(0.016)

    assert getattr(ball, "gravity_well_aura_timer", 0.0) == 5.0
    assert len(world.boosters) == 0

def test_gravity_well_booster_aura_pulls_enemies_and_projectiles():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0, team="blue")
    ball.gravity_well_aura_timer = 5.0
    world.balls.append(ball)

    enemy = MockBall(2, 200.0, 100.0, team="red")
    world.balls.append(enemy)

    # Place a projectile close to the ball
    proj = MockProjectile(90.0, 100.0)
    world.projectiles.append(proj)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.gravity_well_aura_timer < 5.0

    # Enemy should be pulled to the left (x < 200)
    assert enemy.x < 200.0

    # Projectile should be pulled to the right (x > 90)
    assert proj.x > 90.0
