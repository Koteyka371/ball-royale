import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockEntity:
    def __init__(self, id, x, y, kind="booster", ball_type="booster", active=True):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = ball_type
        self.active = active
        self.radius = 15.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.speed = 10.0
        self.slow_timer = 0.0
        self.poison_timer = 0.0
        self.confusion_timer = 0.0
        self.base_speed = 10.0
        self.perception_radius = 500.0

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters is not None else []
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": self.boosters, "traps": []}

def test_cursed_booster():
    booster = MockEntity(10, 0, 0, kind="cursed_booster")
    arena = MockArena(hazards=[booster])
    ball = MockBall(1, 0, 0)
    world = MockWorld(arena, [ball], boosters=[booster])

    action = Action(ball, world)
    action._base_speed_set = True
    action.execute("collect_booster", 1.0)

    # Assert debuffs applied
    assert ball.slow_timer == 5.0
    assert ball.poison_timer == 5.0
    assert ball.confusion_timer == 5.0

    # Assert booster removed
    assert len(world.boosters) == 0
    assert len(world.arena.hazards) == 0
