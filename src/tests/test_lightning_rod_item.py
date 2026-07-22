import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600
        self.weather = "thunderstorm"
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.boosters = []
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": self.boosters}
    def _collect_booster(self, ball, booster):
        pass

class MockEntity:
    def __init__(self, kind):
        self.kind = kind
        self.x = 100
        self.y = 100
        self.radius = 10.0

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100
        self.y = 100
        self.radius = 10.0
        self.team = "A"
        self.alive = True
        self.ball_type = "base"
        self.hp = 100
        self.max_hp = 100
        self.inventory = []
        self.intangible = False
        self.intangible_timer = 0.0

def test_lightning_rod_item():
    world = MockWorld()
    ball = MockBall()
    world.balls = [ball]
    action = Action(ball, world)

    item = MockEntity("lightning_rod_item")
    world.boosters.append(item)

    # 1. Collect
    action.execute("collect_booster", 0.1)

    assert "lightning_rod_item" in ball.inventory
    assert len(world.boosters) == 0

    # 2. Use
    action.execute("attack", 0.1)
    assert "lightning_rod_item" not in ball.inventory

    rods = [h for h in world.arena.hazards if getattr(h, "kind", "") == "deployable_lightning_rod"]
    assert len(rods) == 1

    rod = rods[0]
    assert getattr(rod, "duration", 0) == 15.0
    assert getattr(rod, "charge", -1) == 0.0
    assert getattr(rod, "max_charge", -1) == 100.0
