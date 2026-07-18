import pytest
import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.id = id
        self.hp = 100.0
        self.alive = True
        self.speed = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.ball_type = "default"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 10.0
        self.traits = []

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()

    def get_nearby_entities(self, b, r):
        return {"enemies": [e for e in self.balls if getattr(e, "team", None) != getattr(b, "team", None)], "allies": [e for e in self.balls if getattr(e, "team", None) == getattr(b, "team", None) and e.id != getattr(b, "id", None)]}

def test_enemy_tether_booster():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, "team1")
    ally = MockBall(2, 10, 10, "team1")
    enemy = MockBall(3, 100, 0, "team2")

    booster = MockBooster("enemy_tether_booster", 5, 0)
    world.balls = [b1, ally, enemy]
    world.boosters = [booster]

    action = Action(b1, world)
    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: [enemy]

    action._collect_booster(0.1)

    assert booster not in world.boosters
    assert getattr(enemy, "enemy_tether_timer", 0.0) == 10.0
    assert getattr(enemy, "enemy_tether_target", None) == ally

    enemy_action = Action(enemy, world)
    enemy_hp = enemy.hp
    enemy_x = enemy.x

    # Tick enemy
    enemy_action.execute("idle", 0.1)

    # Enemy should take 10.0 * 0.1 damage
    assert enemy.hp < enemy_hp
    assert enemy.enemy_tether_timer < 10.0
    # Enemy should be pulled towards ally (ally is at x=10, enemy at x=100)
    assert enemy.x < enemy_x
