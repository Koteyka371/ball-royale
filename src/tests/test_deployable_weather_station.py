import pytest
from ai.action import Action
class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.inventory = []
        self.team = "player"
        self.hp = 100
        for k, v in kwargs.items():
            setattr(self, k, v)
class MockHazard:
    def __init__(self, kind, x, y, duration=5.0, radius=50.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.duration = duration
        self.radius = radius
        self.active = True
        self.damage = 0.0
        self.id = 999
class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r): return x, y, False
    def update_zone(self, tick, delta): pass
class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
def test_fake_weather_station():
    world = MockWorld()
    b = MockBall(inventory=["deployable_fake_weather_station"])
    action = Action(b, world)
    action.execute("attack", 1.0)
    assert "deployable_fake_weather_station" not in b.inventory

    assert any(getattr(h, "kind", "") == "deployable_fake_weather_station" for h in world.arena.hazards)

def test_fake_weather_station_emp():
    world = MockWorld()
    b = MockBall(id=1, team="player")
    enemy = MockBall(id=2, team="enemy", hp=100)
    world.balls = [b, enemy]

    hazard = MockHazard("deployable_fake_weather_station", 0.0, 0.0, duration=60.0, radius=150.0)
    hazard.owner_id = 1
    hazard.capture_progress = 90.0
    world.arena.hazards = [hazard]

    action = Action(b, world)
    action.execute("attack", 1.0)

    # 20.0 * 1.0 = 20.0, 90 + 20 = 110 >= 100
    assert not hazard.active
    assert enemy.hp == 70.0
    assert enemy.speed_debuff_timer == 5.0
    assert enemy.speed_debuff_multiplier == 0.5

    event_types = [e["type"] for e in world.events]
    assert "emp_pulse_hit" in event_types
