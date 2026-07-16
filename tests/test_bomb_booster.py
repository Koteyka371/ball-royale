import pytest
import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.alive = True
        self.speed = 100.0
        self.bomb_booster_timer = 0.0
        self.time_bomb_timer = 0.0
        self.time_bomb_attacker_id = None
        self.ball_type = team
        self.team = team
        self.status_effects = []
        self.inventory = []
        self.combo_count = 0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.active = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []

    def _deal_damage(self, attacker, target):
        target.hp -= getattr(attacker, "damage", 10.0)

def test_bomb_plant_and_explode():
    attacker = MockBall(1, 100, 100, team="blue")
    target = MockBall(2, 110, 110, team="red")
    ally_of_target = MockBall(3, 120, 120, team="red")
    enemy_of_target = MockBall(4, 120, 120, team="blue")
    far_ally = MockBall(5, 500, 500, team="red")

    world = MockWorld()
    world.balls = [attacker, target, ally_of_target, enemy_of_target, far_ally]

    attacker.bomb_booster_timer = 10.0

    action_attacker = Action(attacker, world)
    action_target = Action(target, world)

    action_attacker._attempt_damage(attacker, target)

    assert target.hp < 100.0
    assert target.time_bomb_timer == 5.0
    assert target.time_bomb_attacker_id == attacker.id
    assert attacker.bomb_booster_timer == 0.0 # consumed

    target.time_bomb_timer = 0.1
    action_target.execute("idle", 0.5)

    assert target.hp <= 40.0 # base 100 - damage(10) - explosion(50) = 40
    assert ally_of_target.hp == 50.0 # caught in blast
    assert enemy_of_target.hp == 100.0 # not hit
    assert far_ally.hp == 100.0 # too far

def test_bomb_booster_collect():
    collector = MockBall(1, 100, 100, team="blue")
    collector.radius = 10.0
    collector.radius = 10.0
    booster = MockBooster("bomb_booster", 100, 100)
    booster.radius = 10.0
    booster.radius = 10.0
    world = MockWorld()
    world.balls = [collector]
    world.boosters = [booster]

    action = Action(collector, world)
    action.execute("collect_booster", 1.0)

    assert collector.bomb_booster_timer == 10.0
    assert len(world.boosters) == 0
