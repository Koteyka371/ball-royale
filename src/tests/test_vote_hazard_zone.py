import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import pytest

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []

    def add_event(self, kind, data):
        self.events.append({"type": kind, "data": data})

def test_global_hazard_vote():
    from system.crowd_system import CrowdSystem

    world = MockWorld()
    system = CrowdSystem(world)

    system.active_vote = {
        "type": "global_hazard_zone",
        "options": ["low_gravity", "slippery_ice"]
    }
    system.votes = {"low_gravity": 10, "slippery_ice": 0}

    class MockBall:
        def __init__(self):
            self.alive = True
            self.ball_type = "player"

    # Resolve the vote
    system._resolve_vote([MockBall()])

    # Check if the correct event was fired
    hazard_events = [e for e in world.events if e["type"] == "spawn_hazard"]
    assert len(hazard_events) > 0
    event = hazard_events[0]["data"]
    assert event["kind"] == "low_gravity"
    assert event["x"] == 500
    assert event["y"] == 500
    assert event["radius"] == 1000
