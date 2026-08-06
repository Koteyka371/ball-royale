import pytest
from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.ball_type = team

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.active = True

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards else []

class MockWorld:
    def __init__(self, balls=None, boosters=None, arena=None):
        self.balls = balls if balls else []
        self.boosters = boosters if boosters else []
        self.arena = arena

def test_magnetic_field_booster_collection():
    ball = MockEntity(1, 0, 0, "player")
    ball.radius = 10.0

    booster = MockBooster(5, 5, "magnetic_field_booster")
    arena = MockArena([booster])
    world = MockWorld([ball], [booster], arena)

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters

    # Collect booster
    action._collect_booster(0.1)

    assert getattr(ball, "magnetic_field_timer", 0.0) == 15.0
    assert not booster.active
    assert booster not in world.boosters
    assert booster not in arena.hazards

def test_magnetic_field_timer_effect():
    ball = MockEntity(1, 0, 0, "player")
    ball.magnetic_field_timer = 5.0

    enemy = MockEntity(2, 50, 0, "enemy")
    ally = MockEntity(3, -50, 0, "player")
    booster = MockBooster(0, 50, "health_booster")

    world = MockWorld([ball, enemy, ally], [booster])
    action = Action(ball, world)

    action.execute("idle", 0.1)

    assert ball.magnetic_field_timer == 4.9

    # Enemy should be repelled (pushed away from ball)
    assert enemy.x > 50
    assert enemy.y == 0

    # Ally should not be affected
    assert ally.x == -50
    assert ally.y == 0

    # Booster should be pulled (closer to ball)
    assert booster.x == 0
    assert booster.y < 50
