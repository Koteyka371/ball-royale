import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai')))
from action import Action

class MockEntity:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.hp = 100
        self.ball_type = "basic"
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100
        self.__dict__.update(kwargs)

    def get(self, k, d=None):
        return getattr(self, k, d)

class MockWorld:
    def __init__(self):
        self.next_id = 9999
        self.hazards = []
        self.balls = []
        self.boosters = []
        self.events = []
        self.arena = type('Arena', (), {
            'hazards': [],
            'weather': 'heavy_rain',
            'is_raining': True,
            'is_snowing': False,
            'is_ice': False,
            'width': 1000,
            'height': 1000,
            'wind_dx': 0.0,
            'wind_dy': 0.0
        })()

    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters, "enemies": []}

def test_umbrella_booster():
    b = MockEntity(id=1, x=10, y=10, team='t1')
    w = MockWorld()
    w.balls.append(b)
    bst = MockEntity(id=2, x=10, y=10, kind="umbrella_booster")
    w.boosters.append(bst)

    a = Action(b, w)
    a._get_boosters = lambda: [bst]
    a.execute("collect_booster", 0.1)
    a.execute("idle", 0.1)

    assert getattr(b, "umbrella_booster_timer", 0) > 0, "Timer not set"
    assert len(w.boosters) == 0, "Booster not removed"
    assert "umbrella_booster" in getattr(b, "inventory", []), "Not in inventory"

def test_snow_globe_booster():
    b = MockEntity(id=1, x=10, y=10, team='t1', frozen_timer=5.0)
    w = MockWorld()
    w.balls.append(b)
    bst = MockEntity(id=2, x=10, y=10, kind="snow_globe_booster")
    w.boosters.append(bst)

    a = Action(b, w)
    a._get_boosters = lambda: [bst]
    a.execute("collect_booster", 0.1)
    a.execute("idle", 0.1)

    assert getattr(b, "snow_globe_booster_timer", 0) > 0, "Timer not set"
    assert b.frozen_timer == 0.0, "Freeze timer not cleared"
    assert len(w.boosters) == 0, "Booster not removed"
    assert "snow_globe_booster" in getattr(b, "inventory", []), "Not in inventory"
