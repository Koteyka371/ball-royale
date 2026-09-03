
import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.has_pet = False
        self.pet_type = ""
        self.cosmetic = "aura_drain_pet"
        self.speed = 100.0
        self.base_speed = 100.0
        self.aura_intensity = 0.0

class MockHazard:
    def __init__(self, id, x, y, kind, owner_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.owner_id = owner_id

class MockArena:
    def __init__(self):
        self.hazards = []
        self.items = []
        self.gravity_y = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.projectiles = []
        self.arena = MockArena()
        self.boosters = []
        self.width = 1000
        self.height = 1000

def test_aura_drain_pet():
    b1 = MockBall(1, 0, 0, 1)
    b2 = MockBall(2, 50, 0, 2)
    b2.aura_intensity = 5.0

    w = MockWorld()
    w.balls = [b1, b2]

    a1 = Action(b1, w)

    # First tick spawns pet
    b1.vx, b1.vy = 0, 0
    b1.mass = 1
    b1.action = "idle"
    a1.execute("move", 1.0)

    assert b1.has_pet
    assert b1.pet_type == "aura_drain"
    assert len(w.arena.hazards) == 1

    # Simulate another tick so pet drains aura
    # Force pet near enemy for drain test
    w.arena.hazards[0].x = 50
    w.arena.hazards[0].y = 0

    a1.execute("move", 1.0)

    assert b2.aura_intensity < 5.0
    assert b1.speed > 100.0
    assert b1.base_speed > 100.0
