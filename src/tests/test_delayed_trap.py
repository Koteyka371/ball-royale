import pytest
from ai.action import Action

class DummyBall:
    def __init__(self, x, y, id=1, team=1):
        self.x = x
        self.y = y
        self.id = id
        self.team = team
        self.alive = True
        self.radius = 10.0
        self.hp = 100.0
        self.ball_type = "player"

class DummyHazard:
    def __init__(self, kind, x, y, radius, owner_id=None):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.owner_id = owner_id
        self.triggered = False
        self.explosion_timer = 0.0

class DummyArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

class DummyWorld:
    def __init__(self, balls=None, hazards=None):
        self.arena = DummyArena(hazards or [])
        self.balls = balls or []
        self.events = []
    def add_event(self, t, d):
        self.events.append({"type": t, "data": d})

def test_delayed_explosive_trap_triggers_and_pulls():
    ball = DummyBall(x=50.0, y=50.0, id=1, team=1)
    trap = DummyHazard(kind="delayed_explosive_trap", x=100.0, y=50.0, radius=100.0, owner_id=2)
    world = DummyWorld(balls=[ball], hazards=[trap])
    action = Action(ball, world)

    # Initial trigger
    action.execute("idle", 0.1)
    assert getattr(trap, "triggered", False) == True

    initial_x = ball.x
    action.execute("idle", 0.1)
    assert getattr(trap, "explosion_timer", 0.0) > 0.0
    # Check if pulled towards hazard (x=100, y=50)
    assert ball.x > initial_x

def test_delayed_explosive_trap_explodes():
    ball1 = DummyBall(x=50.0, y=50.0, id=1, team=1)
    ball2 = DummyBall(x=120.0, y=50.0, id=2, team=2) # Enemy
    trap = DummyHazard(kind="delayed_explosive_trap", x=100.0, y=50.0, radius=100.0, owner_id=3)
    trap.triggered = True
    trap.explosion_timer = 2.9
    world = DummyWorld(balls=[ball1, ball2], hazards=[trap])
    action = Action(ball1, world)

    action.execute("idle", 0.2)
    # Explodes
    assert trap not in world.arena.hazards
    assert any(e["type"] == "explosion" for e in world.events)
    # Enemy takes damage
    assert ball2.hp == 50.0
    # Enemy is knocked back (x > 120)
    assert ball2.x > 120.0
