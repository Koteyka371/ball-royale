import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.danger_grid = {}

class MockEntity:
    def __init__(self, e_id, e_type, x, y, team):
        self.id = e_id
        self.ball_type = e_type
        self.team = team
        self.x = x
        self.y = y
        self.hp = 100
        self.alive = True
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.suspended_projectiles = []
        self.state_history = []
        self.intangible = False

class MockBooster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "tracker_booster"

class MockWorld:
    def __init__(self):
        self.next_id = 9999
        self.hazards = []
        self.boosters = []
        self.balls = []
        self.arena = MockArena()
        self.tick = 1
        self.time = 1.0
        self.danger_grid = {}

    def get_arena(self):
        return self.arena
    def get_nearby_entities(self, ball, radius):
        import math
        return {
            "enemies": [b for b in self.balls if b != ball and b.team != ball.team and math.hypot(b.x - ball.x, b.y - ball.y) <= radius],
            "boosters": [b for b in self.boosters if math.hypot(b.x - ball.x, b.y - ball.y) <= radius]
        }

def test_tracker_booster():
    w = MockWorld()
    b1 = MockEntity(1, "basic", 0, 0, "team1")
    b1.speed = 2.0
    b2 = MockEntity(2, "basic", 100, 100, "team2")
    b3 = MockEntity(3, "basic", 500, 500, "team2")
    w.balls = [b1, b2, b3]

    booster = MockBooster(5, 5)
    w.boosters.append(booster)

    a = Action(b1, w)
    a._get_boosters = lambda: [booster]
    a._collect_booster(0.0)
    a.execute("idle", 0.1)

    assert getattr(b1, "tracker_booster_timer", 0.0) == 19.9
    assert getattr(b1, "tracker_booster_target", None) == 2
    assert len(w.boosters) == 0

    class StealthZone:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.radius = 50.0
            self.kind = "stealth_zone"
            self.is_disabled_by_flare = False

    sz = StealthZone(100, 100)
    w.arena.hazards.append(sz)

    enemies = a._get_enemies()
    assert b2 in enemies
    assert b3 not in enemies
