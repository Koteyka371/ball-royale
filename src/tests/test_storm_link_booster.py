from ai.action import Action
import math
import pytest

class MockBall:
    def __init__(self, team="A"):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 2.0
        self.base_speed = 2.0
        self.team = team
        self.ball_type = "normal"
        self.max_stamina = 100
        self.stamina = 100
        self.traits = []
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.base_damage = 10
        self.original_base_damage = 10
        self.weather_immunity_timer = 0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 200
        self.invisible = False

class MockBooster:
    def __init__(self, kind):
        self.x = 10.0
        self.y = 0.0
        self.kind = kind
        self.radius = 15.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b.team != entity.team], "allies": [], "hazards": []}

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_storm_link_booster_collection_and_tether():
    b = MockBall("A")
    e = MockBall("B")
    e.x = 100.0
    w = MockWorld()
    w.balls = [b, e]
    booster = MockBooster("storm_link_booster")
    w.boosters = [booster]

    action = Action(b, w)
    action._get_boosters = lambda: w.boosters
    action._get_enemies = lambda: [e]

    action._collect_booster(0.016)

    assert getattr(b, "storm_link_timer", 0) == 5.0
    assert getattr(b, "storm_link_target", None) == e
    assert booster not in w.boosters

def test_storm_link_booster_tick():
    b = MockBall("A")
    e = MockBall("B")
    b.x = 0.0
    e.x = 100.0
    w = MockWorld()
    w.balls = [b, e]

    action = Action(b, w)
    b.storm_link_timer = 5.0
    b.storm_link_target = e

    initial_hp_b = b.hp
    initial_hp_e = e.hp

    action.execute("idle", 0.016)

    # Should take damage
    assert b.hp < initial_hp_b
    assert e.hp < initial_hp_e

    # Should pull towards each other
    assert b.x > 0.0
    assert e.x < 100.0

    # Check speed boost when moving same direction
    b.x = 0.0
    b.y = 0.0
    e.x = 100.0
    e.y = 0.0
    b.vx = 100.0
    e.vx = 100.0
    b.storm_link_timer = 5.0

    action.execute("idle", 0.016)

    # Pull should be applied, but they also get a huge boost in +X
    # Normal pull: b.x increases by 200*0.016*0.5 = 1.6, e.x decreases by 1.6
    # Boost: both get +400*0.016 = 6.4 in +X
    assert b.x > 5.0  # 1.6 + 6.4 = 8.0
    assert e.x > 100.0 # -1.6 + 6.4 = 104.8
