import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.events = []
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

    def _deal_damage(self, attacker, target, amount=10.0):
        target.hp -= amount

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockHazard:
    def __init__(self, kind, x, y, radius, damage=0.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.active = True

class MockBall:
    def __init__(self, team, x, y):
        self.id = id(self)
        self.team = team
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.phase_booster_timer = 0.0

def test_phase_booster_collection():
    world = MockWorld()
    ball = MockBall("red", 500, 500)
    world.balls.append(ball)

    booster = MockHazard("phase_booster", 500, 500, 15)
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert getattr(ball, "phase_booster_timer", 0.0) == 9.0 # 10.0 - 1.0 delta from execute
    assert len(world.boosters) == 0

def test_phase_booster_prevents_dealing_damage():
    world = MockWorld()
    attacker = MockBall("red", 500, 500)
    attacker.phase_booster_timer = 5.0

    target = MockBall("blue", 500, 500)
    world.balls.extend([attacker, target])

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    assert target.hp == 100.0

def test_phase_booster_ignores_hazards():
    world = MockWorld()
    ball = MockBall("red", 500, 500)
    ball.phase_booster_timer = 5.0

    hazard = MockHazard("spikes", 500, 500, 20.0, damage=10.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    # Should not take damage from spikes since we are ignoring hazards
    assert ball.hp == 100.0

def test_phase_booster_wall_clamp():
    world = MockWorld()
    ball = MockBall("red", -50, 500) # out of bounds
    ball.phase_booster_timer = 5.0

    action = Action(ball, world)
    bounced = action._clamp_position()

    # Should not be clamped because phase_booster allows passing walls
    assert bounced == False
    assert ball.x == -50
