import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team=1):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.alive = True
        self.radius = 10.0
        self.is_intangible = False
        self.speed = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.bounces_left = 3
        self.max_hp = 100
        self.chain_lightning_timer = 10.0
        self.damage = 10.0

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10.0

    def get(self, key, default):
        return getattr(self, key, default)

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.items = []

class MockWorld:
    def __init__(self, balls, arena, boosters):
        self.balls = balls
        self.entities = balls
        self.arena = arena
        self.boosters = boosters
        self.events = []

def test_storm_caller_booster():
    ball = MockBall(1, 0, 0, 1)
    target1 = MockBall(2, 50, 0, 2)
    target2 = MockBall(3, 100, 0, 2)

    booster = MockBooster(0, 0, "storm_caller_booster")
    world = MockWorld([ball, target1, target2], MockArena([booster]), [booster])
    action = Action(ball, world)

    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: [target1, target2]

    action._collect_booster(0.1)
    assert getattr(ball, "storm_caller_timer", 0.0) == 15.0

    # Ensure booster was removed
    assert booster not in world.boosters
    assert booster not in world.arena.hazards
