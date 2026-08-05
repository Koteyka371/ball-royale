import pytest
import math
import random
from ai.game_modes import EscortMode

class MockPayload:
    def __init__(self):
        self.x = 500.0
        self.y = 500.0
        self.team = "Defenders"
        self.alive = True
        self.ball_type = "payload"

class MockBall:
    def __init__(self, team, x, y):
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.ball_type = "normal"
        self.shield = 50.0
        self.hp = 100.0
        self.max_hp = 100.0

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

def test_payload_emp_shield_steal_attackers_defenders(monkeypatch):
    mode = EscortMode()
    payload = MockPayload()
    mode.payload = payload

    attacker_1 = MockBall("Attackers", 500.0, 400.0) # Dist 100
    attacker_1.shield = 40.0

    attacker_2 = MockBall("Attackers", 500.0, 900.0) # Dist 400 (Out of range)
    attacker_2.shield = 60.0

    defender_1 = MockBall("Defenders", 500.0, 600.0) # Dist 100

    defender_2 = MockBall("Defenders", 500.0, 550.0) # Dist 50

    balls = [payload, attacker_1, attacker_2, defender_1, defender_2]
    world = MockWorld()

    # We want random.random() to always return a value < 0.3 for this test
    monkeypatch.setattr(random, "random", lambda: 0.1)

    # Fast forward the timer to trigger the EMP
    mode.random_emp_timer = 14.99

    mode.tick(world, balls, delta=0.02)

    # The EMP triggers.
    # Attacker 1 is in range, so it loses 40 shield. Stolen_shields = 40.
    assert attacker_1.shield == 0.0

    # Attacker 2 is out of range, shield remains 60.
    assert attacker_2.shield == 60.0

    # Defender 1 and 2 are in range, so they split 40 shield -> 20 each.
    # New max_hp and hp should be 100 + 20 = 120.
    assert defender_1.max_hp == 120.0
    assert defender_1.hp == 120.0

    assert defender_2.max_hp == 120.0
    assert defender_2.hp == 120.0

    # Verify events
    emp_events = [e for e in world.events if e["type"] == "emp_shield_steal"]
    assert len(emp_events) == 1
    assert emp_events[0]["data"]["total"] == 40.0
