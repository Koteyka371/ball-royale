import pytest
import sys
sys.path.append('src')

from ai.action import Action

class MockGameMode:
    def __init__(self):
        self.zone_target_x = 600.0
        self.zone_target_y = 600.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.safe_zone_center = (500.0, 500.0)
        self.safe_zone_radius = 200.0
        self.items = []

class MockWorld:
    def __init__(self, boosters, hazards):
        self.boosters = boosters
        self.arena = MockArena(hazards)
        self.game_mode = MockGameMode()
        self.events = []
        self.delta = 0.1

    def add_event(self, t, d):
        self.events.append({"type": t, "data": d})

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0
        self.active = True

class MockBall:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.hp = 100.0
        self.alive = True
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.inventory = []
        self.use_item = True
        self.ball_type = "base"

def test_safe_zone_radar_pickup_and_use():
    booster = MockBooster("safe_zone_radar", 10.0, 10.0)
    world = MockWorld([booster], [])
    ball = MockBall(10.0, 10.0, "p1")
    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters

    action._collect_booster(0.1)

    assert booster not in world.boosters
    assert "safe_zone_radar" in ball.inventory

    # Now use it
    action.execute("idle", 0.1)

    assert "safe_zone_radar" not in ball.inventory
    assert getattr(ball, "safe_zone_radar_timer", 0) > 0
    assert getattr(ball, "safe_zone_radar_target_x", 0) == 600.0
    assert getattr(ball, "safe_zone_radar_target_y", 0) == 600.0

    # Assert event was emitted to show next safe zone
    assert len(world.events) > 0
    radar_events = [e for e in world.events if e.get("type") == "safe_zone_radar_ping" and e.get("data", {}).get("owner_id") == "p1"]
    assert len(radar_events) > 0
    assert radar_events[0]["data"]["x"] == 600.0
    assert radar_events[0]["data"]["y"] == 600.0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
