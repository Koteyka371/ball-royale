import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.items = []
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
        self.active = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.arena = MockArena()
        self.game_mode = None

def test_vacuum_booster():
    world = MockWorld()
    player = MockBall(1, 100.0, 100.0)
    health_booster = MockBooster("health", 100.0, 200.0) # 100 distance
    world.balls.append(player)
    world.boosters.append(health_booster)

    action = Action(player, world)

    # 1. Provide the booster
    vacuum = MockBooster("vacuum_booster", 100.0, 100.0)
    world.boosters.append(vacuum)

    # Collect
    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.1)

    # Needs to be removed from world.boosters
    assert vacuum not in world.boosters
    assert getattr(player, "vacuum_booster_timer", 0.0) > 0.0

    # 2. Execute should pull booster
    orig_booster_y = health_booster.y

    action.execute("idle", 0.1)

    # Booster is at 100, 200. It should be pulled towards player (y should decrease)
    assert health_booster.y < orig_booster_y
