import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.team = team
        self.inventory = []
        self.speed = 100.0
        self.damage = 10.0
        self.perception_radius = 100.0
        self.is_blinded = False
        self.blindness_timer = 0.0

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.radius = 150.0
        self.kind = kind
        self.active = True
        self.owner_id = -1
        self.duration = 10.0
        self.team = "none"

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.arena = MockArena()
        self.boosters = []
        self.tick = 0

def test_eclipse_booster_item_collection():
    ball = MockBall(1, 100, 100)
    world = MockWorld([ball])

    booster = MockHazard(105, 105, "eclipse_booster_item")
    booster.radius = 15.0
    world.boosters.append(booster)

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters

    action._collect_booster(0.1)

    assert "eclipse_booster_item" in ball.inventory
    assert len(world.boosters) == 0

def test_eclipse_booster_item_deployment():
    ball = MockBall(1, 100, 100)
    ball.inventory = ["eclipse_booster_item"]
    ball.use_item = True
    world = MockWorld([ball])

    action = Action(ball, world)

    # We trigger _use_item logic inside execute() by picking a strategy that uses items, but the item usage is checked first
    action.execute("idle", 0.1)

    assert "eclipse_booster_item" not in ball.inventory
    assert len(world.arena.hazards) == 1

    hazard = world.arena.hazards[0]
    assert hazard.kind == "eclipse_booster"
    assert getattr(hazard, "owner_id", -1) == ball.id

def test_eclipse_booster_debuff_enemies():
    ball = MockBall(1, 100, 100, "red")
    enemy = MockBall(2, 105, 105, "blue")

    world = MockWorld([ball, enemy])

    hazard = MockHazard(100, 100, "eclipse_booster")
    hazard.owner_id = 1
    hazard.team = "red"
    world.arena.hazards.append(hazard)

    action = Action(enemy, world)
    action.execute("idle", 0.1)

    # Enemy is debuffed
    assert enemy.speed < 100.0
    assert enemy.damage < 10.0
    assert enemy.is_blinded == True
    assert enemy.perception_radius == 50.0

def test_eclipse_booster_no_debuff_allies():
    ball = MockBall(1, 100, 100, "red")
    ally = MockBall(2, 105, 105, "red")

    world = MockWorld([ball, ally])

    hazard = MockHazard(100, 100, "eclipse_booster")
    hazard.owner_id = 1
    hazard.team = "red"
    world.arena.hazards.append(hazard)

    action = Action(ally, world)
    action.execute("idle", 0.1)

    # Ally is unaffected (or owner)
    assert ally.speed == 100.0
    assert ally.damage == 10.0
    assert ally.is_blinded == False
    assert ally.perception_radius == 100.0
