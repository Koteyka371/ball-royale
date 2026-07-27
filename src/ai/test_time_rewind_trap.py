import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, id, x, y, radius, kind, owner_id):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.owner_id = owner_id
        self.duration = 10.0
        self.last_updated_tick = -1

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.tick = 0
        self.tick_timer = 0.0
        self.events = []

class MockBall:
    def __init__(self, id, x, y, hp, radius):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.radius = radius
        self.alive = True
        self.ball_type = "player"

def test_time_rewind_trap_activation_and_rewind():
    hazard = MockHazard(id=1, x=100.0, y=100.0, radius=20.0, kind="time_rewind_trap", owner_id=2)
    world = MockWorld(MockArena(hazards=[hazard]))
    ball = MockBall(id=1, x=100.0, y=100.0, hp=100.0, radius=10.0)
    world.balls = [ball]
    action = Action(ball, world)

    # Tick 1: Trap activation
    action.execute("idle", 1.0)

    assert hazard.duration == 0.0
    assert getattr(ball, "is_time_rewinding", False) is True
    assert getattr(ball, "time_rewind_timer", 0.0) == 3.0

    state = getattr(ball, "time_rewind_state", {})
    assert abs(state.get("x") - 100.0) < 1.0
    assert abs(state.get("y") - 100.0) < 1.0
    assert state.get("hp") == 100.0

    # Tick 2: Move and take damage
    ball.x = 150.0
    ball.y = 150.0
    ball.hp = 50.0
    world.tick += 1
    action.execute("idle", 2.0)

    assert getattr(ball, "is_time_rewinding", False) is True
    assert getattr(ball, "time_rewind_timer", 0.0) == 1.0
    assert abs(ball.x - 150.0) < 1.0
    assert abs(ball.y - 150.0) < 1.0
    assert ball.hp == 50.0

    # Tick 3: Rewind triggers
    world.tick += 1
    action.execute("idle", 1.0)

    assert getattr(ball, "is_time_rewinding", False) is False
    assert getattr(ball, "time_rewind_timer", 0.0) <= 0.0
    assert abs(ball.x - 100.0) < 2.0
    assert abs(ball.y - 100.0) < 2.0
    assert ball.hp == 100.0
    assert any(e["type"] == "visual_effect" and e["data"]["type"] == "teleport" for e in world.events)
