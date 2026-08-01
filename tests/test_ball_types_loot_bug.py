import pytest
from ai.ball_types_loot_bug import LootBug
from ai.action import Action
import math

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.boosters = boosters if boosters is not None else []

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.speed = 10.0
        self.inventory = []
        self.is_decoy = False

def test_loot_bug_initialization():
    bug = LootBug(1, 10, 10)
    assert bug.is_disguised is True
    assert bug.speed == 0.0
    assert bug.base_speed == 5.0
    assert bug.BALL_TYPE == "loot_bug"

def test_loot_bug_ignored_by_enemies():
    bug = LootBug(1, 10, 10)
    bug.team = "A"

    enemy = MockBall(2, 20, 20, team="B")
    enemy.BALL_TYPE = "enemy"
    enemy.perception_radius = 500

    world = MockWorld(MockArena(), [bug, enemy])
    action = Action(enemy, world)

    enemies = action._get_enemies_internal()
    # Bug is disguised, should not be seen as an enemy
    assert bug not in enemies

def test_loot_bug_is_fake_booster():
    bug = LootBug(1, 10, 10)
    bug.team = "A"
    bug.disguise_type = "hp_booster"

    enemy = MockBall(2, 20, 20, team="B")
    enemy.BALL_TYPE = "enemy"
    enemy.perception_radius = 500

    world = MockWorld(MockArena(), [bug, enemy])
    action = Action(enemy, world)

    boosters = action._get_boosters()
    found = False
    for b in boosters:
        if getattr(b, "kind", "") == "hp_booster" and getattr(b, "bug", None) == bug:
            found = True
            break
    assert found

def test_loot_bug_ambush_transformation():
    bug = LootBug(1, 10, 10)
    bug.team = "A"
    bug.trigger_distance = 60.0

    # Enemy is very close (distance = 20)
    enemy = MockBall(2, 10, 30, team="B")
    enemy.BALL_TYPE = "enemy"

    world = MockWorld(MockArena(), [bug, enemy])
    action = Action(bug, world)

    # Initially disguised
    assert bug.is_disguised is True

    # Execute tick
    action.execute("idle", 0.1)

    # Should have ambushed
    assert bug.is_disguised is False
    assert bug.speed == 5.0
    assert getattr(bug, "speed_multiplier", 1.0) == 1.5
    assert getattr(bug, "speed_multiplier_timer", 0.0) == 2.0
