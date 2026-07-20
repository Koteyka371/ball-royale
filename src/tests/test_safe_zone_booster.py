import pytest

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, boosters, hazards):
        self.boosters = boosters
        self.arena = MockArena(hazards)

    def _deal_damage(self, attacker, target, amount=10.0):
        target.hp -= amount

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0

class MockBall:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.hp = 100.0
        self.alive = True
        self.radius = 10.0

import sys
sys.path.append('src')
from ai.action import Action

def test_safe_zone_booster():
    booster = MockBooster("safe_zone_booster", 10.0, 10.0)
    world = MockWorld([booster], [booster])
    ball = MockBall(10.0, 10.0, "p1")
    action = Action(ball, world)

    # Force booster getter to return our booster
    action._get_boosters = lambda: world.boosters

    # 1. Collect booster
    action._collect_booster(0.1)
    assert getattr(ball, "safe_zone_booster_timer", 0.0) == 10.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

    # 2. Tick to spawn safe zone
    action.execute("idle", 0.1)

    # Check safe zone spawned
    safe_zones = [h for h in world.arena.hazards if getattr(h, "kind", "") == "personal_safe_zone"]
    assert len(safe_zones) == 1
    sz = safe_zones[0]
    assert sz.owner_id == "p1"
    assert abs(sz.x - ball.x) < 0.1
    assert abs(sz.y - ball.y) < 0.1
    assert sz.radius == 40.0

    # 3. Ball moves, safe zone should follow
    ball.x = 20.0
    ball.y = 20.0
    action.execute("idle", 0.1)
    assert abs(sz.x - ball.x) < 0.1
    assert abs(sz.y - ball.y) < 0.1

    # 4. Timer should decrement
    assert ball.safe_zone_booster_timer < 10.0

    # 5. Check hazard immunity
    # We need to simulate the hazard processing loop that applies immunity
    # Let's execute again so it hits personal_safe_zone
    action.execute("idle", 0.1)
    assert getattr(ball, "hazard_immunity_timer", 0.0) >= 0.1

    # Fast forward to end of booster
    ball.safe_zone_booster_timer = 0.0
    sz.duration = 0.0
    action.execute("idle", 0.1)

if __name__ == "__main__":
    pytest.main(["-v", "test_safe_zone_booster.py"])
