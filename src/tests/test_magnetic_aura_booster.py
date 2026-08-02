import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.team = f"team_{id}"
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.arena = MockArena()
        self.game_mode = None

def test_magnetic_aura_booster():
    world = MockWorld()
    player = MockBall(1, 100.0, 100.0)
    enemy = MockBall(2, 200.0, 100.0) # 100 distance
    booster = MockBooster("health", 100.0, 200.0) # 100 distance
    world.balls.extend([player, enemy])
    world.boosters.append(booster)

    action = Action(player, world)

    # 1. Provide the booster
    mag_booster = MockBooster("magnetic_aura_booster", 100.0, 100.0)
    world.boosters.append(mag_booster)

    # Collect
    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.1)

    # Needs to be removed from world.boosters
    assert mag_booster not in world.boosters
    assert getattr(player, "magnetic_aura_timer", 0.0) > 0.0

    # 2. Execute should pull enemy and booster
    orig_enemy_x = enemy.x
    orig_booster_y = booster.y

    action._get_enemies_internal = lambda: [enemy]
    action.execute("idle", 0.1)

    # Player is at 100, 100. Enemy is at 200, 100. It should be pulled towards player (x should decrease)
    assert enemy.x < orig_enemy_x
    # Booster is at 100, 200. It should be pulled towards player (y should decrease)
    assert booster.y < orig_booster_y
