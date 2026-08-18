import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 1
        self.balls = []
        self.events = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

class MockHazard:
    def __init__(self, kind, x, y, radius, active=True, destroyed=False):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = active
        self.destroyed = destroyed

class MockBall:
    def __init__(self, id, hp, max_hp, traits):
        self.id = id
        self.hp = hp
        self.max_hp = max_hp
        self.traits = traits
        self.x = 0
        self.y = 0
        self.alive = True
        self.speed = 100

def test_nanite_swarm_trigger():
    ball = MockBall(1, 25, 100, ["nanite_swarm"])
    world = MockWorld()
    world.balls.append(ball)

    # Add debris
    debris = MockHazard("orbital_debris", 50, 0, 40)
    world.arena.hazards.append(debris)

    action = Action(ball, world)
    action.execute("dummy", 0.1)

    assert getattr(ball, "nanite_swarm_active", False) == True
    assert ball.hp > 25 # Healed
    assert debris.radius < 40 # Consumed

def test_nanite_swarm_not_triggered_above_30_percent():
    ball = MockBall(1, 40, 100, ["nanite_swarm"])
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("dummy", 0.1)

    assert getattr(ball, "nanite_swarm_active", False) == False
    assert ball.hp == 40

def test_nanite_swarm_destroyed_hazard():
    ball = MockBall(1, 25, 100, ["nanite_swarm"])
    world = MockWorld()
    world.balls.append(ball)

    # Add destroyed hazard
    destroyed_hazard = MockHazard("some_trap", 50, 0, 40, active=False, destroyed=True)
    world.arena.hazards.append(destroyed_hazard)

    action = Action(ball, world)
    action.execute("dummy", 0.1)

    assert getattr(ball, "nanite_swarm_active", False) == True
    assert ball.hp > 25
    assert destroyed_hazard.radius < 40
