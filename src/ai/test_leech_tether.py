import pytest
import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action
from ai.ball_types_leech import Leech

class MockBall(Leech):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.team = "team1"
        self.ball_type = "leech"

class MockEnemy:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = "team2"
        self.alive = True
        self.radius = 10.0
        self.ball_type = "enemy"

class MockWorld:
    def __init__(self):
        self.balls = []

    def get_nearby_entities(self, b, r):
        return {"enemies": [e for e in self.balls if getattr(e, "team", "") != getattr(b, "team", "")], "allies": []}

    def _deal_damage(self, attacker, target):
        damage = getattr(attacker, "damage", 10.0)
        target.hp -= damage

def test_leech_lifesteal():
    world = MockWorld()
    leech = MockBall(1, 0, 0)
    enemy = MockEnemy(2, 10, 0)
    world.balls = [leech, enemy]

    action = Action(leech, world)

    leech.hp = 50.0
    leech.damage = 10.0

    action._attempt_damage(leech, enemy)

    # dealt 10 damage, so healed for 20
    assert enemy.hp == 90.0
    assert leech.hp == 70.0

def test_leech_tether():
    world = MockWorld()
    leech = MockBall(1, 0, 0)
    enemy = MockEnemy(2, 50, 0)
    world.balls = [leech, enemy]

    action = Action(leech, world)
    action.execute("use_skill", 1.0)

    assert leech.leech_tether_timer > 0.0
    assert leech.leech_tether_target == enemy

    enemy_hp = enemy.hp
    action.execute("idle", 0.1) # tick

    assert enemy.hp < enemy_hp
    assert getattr(enemy, "stun_timer", 0.0) > 0.0
