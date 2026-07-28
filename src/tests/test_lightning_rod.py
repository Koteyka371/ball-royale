import pytest
from ai.game_modes import LightningStrikeEventMode

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.has_lightning_rod = False
        self.stun_timer = 0.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.boosters = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test_lightning_rod_redirects_strike():
    mode = LightningStrikeEventMode()
    world = MockWorld()

    # Force event to be active and add a strike
    mode.event_active = True
    mode.strikes = [{
        "id": "lightning_test",
        "x": 500,
        "y": 500,
        "radius": 40.0,
        "timer": 0.0,
        "state": "warning"
    }]

    # Create balls
    bearer = MockBall(1, 100, 100, "team_a")
    bearer.has_lightning_rod = True

    enemy = MockBall(2, 700, 700, "team_b")

    balls = [bearer, enemy]

    # Tick to transition state and trigger redirect
    mode.tick(world, balls, delta=0.016)

    # The strike should now be relocated to the enemy
    strike = mode.strikes[0]
    assert strike["state"] == "active"
    assert strike["x"] == 700
    assert strike["y"] == 700

    # The lightning rod should be consumed
    assert not bearer.has_lightning_rod

    # Event should be added
    redirect_events = [e for e in world.events if e["type"] == "lightning_redirect"]
    assert len(redirect_events) == 1
    assert redirect_events[0]["data"]["x"] == 700
    assert redirect_events[0]["data"]["y"] == 700
