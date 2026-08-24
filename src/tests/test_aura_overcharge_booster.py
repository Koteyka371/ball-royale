import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, hp=100.0):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = True
        self.id = 1
        self.team = "player"
        self.aura_overcharge_timer = 0.0

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.radius = 15.0

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters is not None else []
        self.events = []

def test_aura_overcharge_collection():
    ball = MockBall(0, 0)
    booster = MockHazard(10, 10, "aura_overcharge_booster")
    arena = MockArena([booster])
    world = MockWorld(arena, [ball], boosters=[booster])

    action = Action(ball, world)
    action._get_boosters = lambda: [booster]

    # Trigger collection
    action._collect_booster(0.1)

    # Assert booster collected and removed
    assert getattr(ball, "aura_overcharge_timer", 0.0) == 10.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_aura_overcharge_tick():
    ball = MockBall(0, 0, hp=100.0)
    world = MockWorld(MockArena(), [ball])
    action = Action(ball, world)

    # Manually activate the overcharge
    ball.aura_overcharge_timer = 5.0

    action._apply_friendly_aura(0.1)

    # Timer should decrease by 0.1
    assert ball.aura_overcharge_timer == 4.9

    # HP should decrease by 5.0 * 0.1 = 0.5
    assert ball.hp == 99.5
