import pytest
from ai.action import Action

class DummyBall:
    def __init__(self, id, x, y, radius=10.0, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = alive
        self.team = "test"
        self.ball_type = "test"
        self.skills = []
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.current_action = "none"

class DummyHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.active = True

class DummyArena:
    def __init__(self):
        self.hazards = []
        self.items = []
        self.boosters = []

    def clamp_position(self, x, y, radius):
        return x, y, False

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.balls = []
        self.boosters = []
        self.projectiles = []
        self.leaderboard_manager = type('Mock', (), {'data': {'current_season': 4}})()

def test_phase_booster():
    ball = DummyBall(1, 100.0, 100.0)
    world = DummyWorld()
    world.balls.append(ball)

    booster = DummyHazard("phase_booster", 100.0, 100.0)
    world.arena.hazards.append(booster)
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("collect_booster", 0.1)

    assert getattr(ball, "phase_booster_timer", 0.0) > 0.0
    assert booster not in world.arena.hazards

def test_phase_booster_ignores_collisions():
    ball = DummyBall(1, 100.0, 100.0)
    ball.phase_booster_timer = 5.0
    world = DummyWorld()
    world.balls.append(ball)

    # Solid hazard
    wall = DummyHazard("kinetic_absorber", 100.0, 100.0)
    world.arena.hazards.append(wall)

    action = Action(ball, world)
    # _resolve_collisions returns False when phased and does not process
    assert not action._resolve_collisions()
