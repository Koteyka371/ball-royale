import pytest
from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.speed = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "team1"
        self.mass = 1.0

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 100.0
        self.y = 100.0
        self.radius = 15.0
        self.active = True
        self.damage = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000

def test_ghost_booster():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    # Add ghost booster
    booster = MockHazard("ghost_booster")
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.1)

    # Should have collected it
    assert getattr(ball, "ghost_booster_timer", 0.0) > 0.0

    # Check ghost mode active
    assert getattr(ball, "ghost_mode_active", False) == True
    assert getattr(ball, "intangible", False) == True
    assert getattr(ball, "intangible_timer", 0.0) > 0.0
    assert getattr(ball, "is_ghost", False) == True

    # Add hazard
    hazard = MockHazard("damage_zone")
    world.arena.hazards.append(hazard)

    attacker = MockBall()
    attacker.id = 2
    attacker.team = "team2"
    attacker.damage = 50.0

    # attempt damage
    action._attempt_damage_internal(attacker, ball)

    # Should not take damage
    assert ball.hp == 100.0

    # Manually decay the timer
    ball.ghost_booster_timer = 0.05
    action.execute("idle", 0.1)

    # Timer should be 0 and ghost mode false
    assert getattr(ball, "ghost_booster_timer", 1.0) == 0.0
    assert getattr(ball, "ghost_mode_active", True) == False
    assert getattr(ball, "is_ghost", True) == False
