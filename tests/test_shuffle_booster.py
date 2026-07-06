import pytest
from src.ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, x=0, y=0, alive=True, inventory=None, active_skill=None):
        self.x = x
        self.y = y
        self.alive = alive
        self.inventory = inventory if inventory else []
        self.active_skill = active_skill
        self.radius = 10.0
        self.speed = 100
        self.base_speed = 100
        self.hp = 100
        self.perception_radius = 500
        self.skill_timer = 0
        self.skill_cooldown = 10
        self.used_skill_count = 0
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.hp = 100
        self.perception_radius = 500
        self.skill_timer = 0
        self.skill_cooldown = 10
        self.used_skill_count = 0
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.hp = 100
        self.perception_radius = 500
        self.skill_timer = 0
        self.skill_cooldown = 10
        self.used_skill_count = 0
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.hp = 100
        self.perception_radius = 500
        self.skill_timer = 0
        self.skill_cooldown = 10
        self.used_skill_count = 0
        self.vx = 0
        self.vy = 0

class MockBooster:
    def __init__(self, kind, x=0, y=0, radius=300.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.active = True
        self.active = True
        self.active = True

def test_shuffle_booster_collect():
    world = MockWorld()

    player1 = MockBall(x=0, y=0, inventory=["trap"], active_skill="dash")
    player2 = MockBall(x=100, y=0, inventory=["heal"], active_skill="shield")

    world.balls = [player1, player2]

    booster = MockBooster(kind="shuffle_booster", x=0, y=0)
    world.boosters.append(booster)

    action = Action(player1, world)

    # Run _collect_booster logic (which searches boosters from world)
    action._collect_booster(0.1)

    assert booster not in world.boosters
    assert getattr(player1, "shuffle_booster_timer", 0) == 10.0
    assert getattr(player1, "shuffle_booster_target", None) == player2

    # Skills and inventory should be swapped
    assert player1.inventory == ["heal"]
    assert player1.active_skill == "shield"

    assert player2.inventory == ["trap"]
    assert player2.active_skill == "dash"

def test_shuffle_booster_execute_timer():
    world = MockWorld()

    player1 = MockBall(x=0, y=0, inventory=["heal"], active_skill="shield")
    player2 = MockBall(x=100, y=0, inventory=["trap"], active_skill="dash")

    player1.shuffle_booster_timer = 0.5
    player1.shuffle_booster_target = player2

    action = Action(player1, world)

    # execute with 0.4 delta, shouldn't swap yet
    action.execute("none", 0.4)

    assert abs(player1.shuffle_booster_timer - 0.1) < 0.001
    assert player1.inventory == ["heal"]
    assert player2.inventory == ["trap"]

    # execute with 0.2 delta, should reach < 0 and swap back
    action.execute("none", 0.2)

    assert player1.shuffle_booster_timer < 0
    assert getattr(player1, "shuffle_booster_target", None) is None

    assert player1.inventory == ["trap"]
    assert player1.active_skill == "dash"

    assert player2.inventory == ["heal"]
    assert player2.active_skill == "shield"


def test_shuffle_booster_no_damage():
    world = MockWorld()

    player1 = MockBall(x=0, y=0, inventory=["trap"], active_skill="dash")
    player2 = MockBall(x=100, y=0, inventory=["heal"], active_skill="shield")

    world.balls = [player1, player2]

    booster = MockBooster(kind="shuffle_booster", x=0, y=0)
    world.boosters.append(booster)

    action = Action(player1, world)

    initial_hp_p1 = player1.hp
    initial_hp_p2 = player2.hp

    action._collect_booster(0.1)

    assert player1.hp == initial_hp_p1
    assert player2.hp == initial_hp_p2
