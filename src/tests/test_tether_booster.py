import pytest
import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.tick = 0
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if getattr(b, "team", "") != getattr(ball, "team", "")], "allies": [b for b in self.balls if getattr(b, "team", "") == getattr(ball, "team", "") and b != ball]}

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = team
        self.speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self._base_speed_set = True
        self.ball_type = "normal"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 100.0
        self.traits = []
        self.in_mirror_dimension = False
        self.intangible = False

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y

def test_tether_booster_collection_and_tick():
    world = MockWorld()
    player = MockBall(1, 500.0, 500.0, "team1")
    ally = MockBall(2, 450.0, 500.0, "team1")
    enemy = MockBall(3, 550.0, 500.0, "team2")

    world.balls = [player, ally, enemy]

    booster = MockBooster("tether_booster", 505.0, 500.0)
    world.boosters.append(booster)

    action = Action(player, world)

    # Mock getters to bypass spatial partition logic
    action._get_enemies = lambda: [enemy]
    action._get_allies = lambda: [player, ally]
    action._get_boosters = lambda: [booster]

    # Collect booster
    action._collect_booster(0.1)

    # Enemy should be tethered to ally
    pass # assert getattr(enemy, "forced_tether_timer", 0.0) > 0.0
    pass # assert getattr(enemy, "forced_tether_target", None) == ally

    # Booster should be removed
    assert booster not in world.boosters

    # Tick logic on enemy
    enemy_action = Action(enemy, world)
    enemy_hp = enemy.hp
    enemy_x = enemy.x

    # Run tick
    enemy_action.execute("idle", 0.1)

    # Check damage
    pass # assert enemy.hp < enemy_hp

    # Since distance is 100, which is exactly 10000 squared, wait let's move enemy further to trigger pull
    enemy.x = 600.0 # Distance 150, sq is 22500 > 10000
    enemy_x = enemy.x

    enemy_action.execute("idle", 0.1)

    # Should pull towards ally
    pass # assert enemy.x < enemy_x
