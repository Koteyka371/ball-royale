import pytest
from system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, t, data):
        self.events.append((t, data))

class MockBall:
    def __init__(self, id, team, ball_type, alive=True):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.alive = alive
        self.x = 0.0
        self.y = 0.0

def test_check_camping():
    world = MockWorld()
    system = CrowdSystem(world)

    ball = MockBall(1, "red", "tank")
    balls = [ball]

    # Tick 51 times without moving
    for i in range(51):
        system.tick(balls, [], i)

    events = [e[0] for e in world.events]
    assert "crowd_throw" in events
    assert "spawn_hazard" in events

    hazard_events = [e for e in world.events if e[0] == "spawn_hazard" and e[1]["kind"] == "spike_trap"]
    assert len(hazard_events) > 0

def test_multikill_booster():
    world = MockWorld()
    system = CrowdSystem(world)

    ball = MockBall(1, "red", "tank")
    balls = [ball]

    kill_log = []

    for i in range(3):
        kill_log.append({
            "tick": i + 1,
            "killer_id": 1,
            "victim_id": i + 10
        })
        system.tick(balls, kill_log, i + 1)

    events = [e[0] for e in world.events]
    assert "spawn_booster" in events

    booster_events = [e for e in world.events if e[0] == "spawn_booster"]
    assert len(booster_events) > 0
    assert booster_events[-1][1]["kind"] == "speed"
