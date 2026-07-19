import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.tick = 100
        self.arena = MockArena()
        self.boosters = []
        self.events = []
        self.balls = []

class MockBall:
    def __init__(self, id, x, y, team=1):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.speed = 1.0
        self.base_speed = 1.0
        self.team = team
        self.alive = True
        self.last_teleport_tick = 0
        self.quantum_teleporter_booster_timer = 0.0
        self.radius = 10.0

class MockItem:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10.0

def test_collection_quantum_teleporter_booster():
    world = MockWorld()
    ball = MockBall(1, 0, 0)
    action = Action(ball, world)

    booster = MockItem(5, 5, "quantum_teleporter_booster")
    world.boosters.append(booster)

    # Overwrite _get_boosters and _get_enemies for isolation
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._get_allies = lambda: []

    action._collect_booster(0.1)

    assert getattr(ball, "quantum_teleporter_booster_timer", 0.0) == 10.0
    assert len(world.boosters) == 0

def test_quantum_teleporter_booster_timer_decrements():
    world = MockWorld()
    ball = MockBall(1, 0, 0)
    action = Action(ball, world)

    ball.quantum_teleporter_booster_timer = 5.0

    # Let's directly call execute without hazards so it just idles and decrements timer
    action._get_allies = lambda: []
    action._get_enemies = lambda: []
    action._get_boosters = lambda: []

    action.execute("idle", 0.1)

    assert ball.quantum_teleporter_booster_timer < 5.0
