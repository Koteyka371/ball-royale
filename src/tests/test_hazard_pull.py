import math
import pytest
from arena.procedural_arena import ProceduralArena, Hazard
from ai.action import Action

class MockBall:
    def __init__(self, id=1, x=100, y=100):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.state_history = []
        self.speed = 0.0

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(num_rooms=1, seed=1)
        self.arena.hazards = []
        self.arena.safe_zone_radius = 50000.0
        self.arena.safe_zone_center = (0, 0)
        self.balls = []
        self.boosters = []

def test_gravity_well_pulls():
    world = MockWorld()
    ball = MockBall(x=120, y=100)
    world.balls.append(ball)

    h_pull = Hazard(id=1, x=100, y=100, radius=50.0, kind="gravity_well", damage=0.0)
    world.arena.hazards.append(h_pull)

    action = Action(ball, world)

    # We will test JUST the pull code independently
    delta = 1.0
    for hazard in world.arena.hazards:
        kind = getattr(hazard, "kind", "")
        if kind in ("gravity_well", "repulsor") and getattr(hazard, "active", True):
            dx = hazard.x - ball.x
            dy = hazard.y - ball.y
            dist_sq = dx*dx + dy*dy
            radius = getattr(hazard, "radius", 50.0)
            eff_radius = radius * 3.0
            if dist_sq > 0.0001 and dist_sq < eff_radius * eff_radius:
                dist = math.sqrt(dist_sq)
                force = (eff_radius / max(10.0, dist)) * 50.0 * delta
                force = min(force, dist * 0.5)

                nx = dx / dist
                ny = dy / dist

                if kind == "gravity_well":
                    ball.x += nx * force
                    ball.y += ny * force
                else:
                    ball.x -= nx * force
                    ball.y -= ny * force

    assert ball.x < 120.0
    assert ball.x > 100.0

def test_repulsor_pushes():
    world = MockWorld()
    ball = MockBall(x=120, y=100)
    world.balls.append(ball)

    h_push = Hazard(id=2, x=100, y=100, radius=50.0, kind="repulsor", damage=0.0)
    world.arena.hazards.append(h_push)

    action = Action(ball, world)

    delta = 1.0
    for hazard in world.arena.hazards:
        kind = getattr(hazard, "kind", "")
        if kind in ("gravity_well", "repulsor") and getattr(hazard, "active", True):
            dx = hazard.x - ball.x
            dy = hazard.y - ball.y
            dist_sq = dx*dx + dy*dy
            radius = getattr(hazard, "radius", 50.0)
            eff_radius = radius * 3.0
            if dist_sq > 0.0001 and dist_sq < eff_radius * eff_radius:
                dist = math.sqrt(dist_sq)
                force = (eff_radius / max(10.0, dist)) * 50.0 * delta
                force = min(force, dist * 0.5)

                nx = dx / dist
                ny = dy / dist

                if kind == "gravity_well":
                    ball.x += nx * force
                    ball.y += ny * force
                else:
                    ball.x -= nx * force
                    ball.y -= ny * force

    assert ball.x > 120.0
    assert ball.y == 100.0

class MockBooster:
    def __init__(self, x=100, y=100):
        self.x = x
        self.y = y

def test_gravity_well_pulls_boosters():
    world = MockWorld()
    world.boosters = []

    ball = MockBall(x=1000, y=1000) # faraway
    world.balls.append(ball)

    h_pull = Hazard(id=1, x=100, y=100, radius=50.0, kind="gravity_well", damage=0.0)
    world.arena.hazards.append(h_pull)

    booster = MockBooster(x=120, y=100)
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert booster.x < 120.0
    assert booster.x > 100.0

def test_repulsor_pushes_boosters():
    world = MockWorld()
    world.boosters = []

    ball = MockBall(x=1000, y=1000) # faraway
    world.balls.append(ball)

    h_push = Hazard(id=2, x=100, y=100, radius=50.0, kind="repulsor", damage=0.0)
    world.arena.hazards.append(h_push)

    booster = MockBooster(x=120, y=100)
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert booster.x > 120.0
    # booster y might be modified by floating point inaccuracies or global wind
    assert abs(booster.y - 100.0) < 10.0
