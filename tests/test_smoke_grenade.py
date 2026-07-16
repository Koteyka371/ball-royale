import pytest
from src.ai.perception import Perception

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena or MockArena()

    def get_nearby_entities(self, ball, radius):
        # We need this to return a dictionary like {"enemies": [...], "allies": [...], "boosters": [...], "traps": [...]}
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}

class MockBall:
    def __init__(self, x=0, y=0, radius=20, team="red"):
        self.x = x
        self.y = y
        self.radius = radius
        self.team = team
        self.perception_radius = 250.0
        self.cosmetic = ""

class MockSmokeGrenade:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = "smoke_grenade"

def test_smoke_grenade_perception_radius():
    b1 = MockBall(0, 0, team="red")
    smoke = MockSmokeGrenade(0, 0, 50)
    world = MockWorld(MockArena([smoke]))

    passed_radius = []
    def mock_get(b, r):
        passed_radius.append(r)
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}
    world.get_nearby_entities = mock_get

    p = Perception(b1, world)
    p.scan()
    assert passed_radius[0] <= 50.0

def test_smoke_grenade_line_of_sight():
    b1 = MockBall(0, 0, team="red")
    b2 = MockBall(100, 100, team="blue")
    smoke = MockSmokeGrenade(0, 0, 50)
    world = MockWorld(MockArena([smoke]))

    def mock_get(b, r):
        # Note: b2 is outside perception if r=50, but let's see if intersects_smoke works
        return {"enemies": [b2], "allies": [], "boosters": [], "traps": []}
    world.get_nearby_entities = mock_get

    p = Perception(b1, world)
    data = p.scan()
    # Should not see b2 because b1 is in smoke, also line of sight goes through smoke
    assert len(data["enemies"]) == 0
