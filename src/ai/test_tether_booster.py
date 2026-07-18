from ai.action import Action
import pytest

class MockBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 2.0
        self.team = "A"
        self.ball_type = "normal"
        self.max_stamina = 100
        self.stamina = 100
        self.base_speed = 2.0
        self.traits = []
        self.in_mirror_dimension = False
        self.intangible = False
        self.hp = 100
        self.max_hp = 100
        self.vx = 0
        self.vy = 0

class MockBooster:
    def __init__(self, kind):
        self.x = 10
        self.y = 0
        self.kind = kind
        self.radius = 15

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 500

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if getattr(b, "team", getattr(b, "ball_type", "")) != entity.team], "allies": [], "hazards": []}

def test_tether_booster_collection_and_pull():
    b = MockBall()
    e = MockBall()
    e.team = "B"
    e.x = 100
    e.y = 0
    w = MockWorld()
    w.balls = [b, e]
    booster = MockBooster("tether_booster")
    w.boosters = [booster]

    action = Action(b, w)

    # Mock _get_boosters to return our list instead of relying on real spatial lookups
    action._get_boosters = lambda: w.boosters

    # Run _collect_booster
    action._collect_booster(0.016)

    assert hasattr(b, "tether_booster_timer"), "Timer should be set"
    assert b.tether_booster_timer == 3.0, "Timer should start at 3.0"
    assert b.tether_booster_target == e, "Target should be the enemy"
    assert len(w.boosters) == 0, "Booster should be removed from world"

    # Now run execute tick to verify pull logic
    initial_e_x = e.x
    action.execute("idle", 0.016)

    assert b.tether_booster_timer < 3.0, "Timer should decrease"
    assert e.x < initial_e_x, "Enemy should have been pulled closer (x decreased)"
