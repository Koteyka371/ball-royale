from ai.action import Action
from ai.perception import Perception
from arena.arena_types import DayNightArena

class MockBall:
    def __init__(self, t="vampire", p_rad=300.0, speed=100.0, damage=10.0):
        self.ball_type = t
        self.perception_radius = p_rad
        self.speed = speed
        self.base_speed = speed
        self.damage = damage
        self.base_damage = damage
        self._base_speed_set = True
        self.x = 0
        self.y = 0
        self.radius = 20
        self.traits = []

class MockWorld:
    def __init__(self, night=True):
        self.arena = DayNightArena()
        self.arena.is_night = night
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}

def test_vampire_stats_at_night():
    w = MockWorld(night=True)
    b = MockBall("vampire")
    a = Action(b, w)
    a.execute("idle", 0.016)
    # In night, vampire speed & damage should be 1.5x base
    assert b.speed == 150.0
    assert b.damage == 15.0

def test_normal_stats_at_night():
    w = MockWorld(night=True)
    b = MockBall("tank")
    a = Action(b, w)
    a.execute("idle", 0.016)
    # In night, normal ball speed should be base, damage base
    assert b.speed == 100.0
    assert b.damage == 10.0

def test_vampire_perception_at_night():
    w = MockWorld(night=True)
    b = MockBall("vampire")
    p = Perception(b, w)
    p.scan() # scan reads perception_radius internally but doesn't modify the ball, it relies on local var.
    # We can just run it to ensure no exceptions.

def test_assassin_stats_at_night():
    w = MockWorld(night=True)
    b = MockBall("assassin")
    a = Action(b, w)
    a.execute("idle", 0.016)
    assert b.speed == 120.0
    assert b.damage == 15.0
    assert getattr(b, "has_stealth_drone", False) == True

def test_paladin_stats_during_day():
    w = MockWorld(night=False)
    b = MockBall("paladin")
    a = Action(b, w)
    a.execute("idle", 0.016)
    assert b.speed == 120.0
    assert b.damage == 15.0

def test_assassin_stats_during_day():
    w = MockWorld(night=False)
    b = MockBall("assassin")
    a = Action(b, w)
    a.execute("idle", 0.016)
    assert b.speed == 100.0
    assert b.damage == 12.0
