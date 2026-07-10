import pytest
from ai.action import Action
from ai.ball_types_broodmother import Broodmother
from ai.ball_types_broodling import Broodling

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockBooster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.kind = "health_pack"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.next_id = 99

    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters, "hazards": self.arena.hazards}

    def _collect_booster(self, ball, item):
        pass

def test_broodmother_summon():
    world = MockWorld()
    broodmother = Broodmother(1, 100, 100)
    broodmother.team = "swarm"
    broodmother.ball_type = "broodmother"
    world.balls.append(broodmother)

    action = Action(broodmother, world)
    broodmother.skill = "summon_broodlings"
    broodmother.skill_timer = 0
    action.execute("use_skill", 0.016)

    # Check if broodlings were summoned
    assert len(world.balls) > 1
    broodling = world.balls[1]
    assert getattr(broodling, "ball_type", "") == "broodling"
    assert broodling.team == "swarm"

def test_broodling_collects_item():
    world = MockWorld()
    broodling = Broodling(2, 50, 50)
    broodling.ball_type = "broodling"
    world.balls.append(broodling)

    booster = MockBooster(55, 55)
    world.boosters.append(booster)

    action = Action(broodling, world)
    action.execute("idle", 0.16)

    # The broodling should have moved towards the booster and collected it
    assert len(world.boosters) == 0

def test_broodling_heals_ally():
    world = MockWorld()
    broodmother = Broodmother(1, 100, 100)
    broodmother.team = "swarm"
    broodmother.hp = 10 # injured
    world.balls.append(broodmother)

    broodling = Broodling(2, 105, 105)
    broodling.team = "swarm"
    broodling.ball_type = "broodling"
    world.balls.append(broodling)

    action = Action(broodling, world)
    action.execute("idle", 0.16)

    # Broodling should heal broodmother and die
    assert broodmother.hp == 30.0
    assert not broodling.alive
