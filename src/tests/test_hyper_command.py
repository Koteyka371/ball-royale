import pytest
from system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []
        self.leaderboard_manager = None

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, type_name):
        self.ball_type = type_name
        self.alive = True
        self.aggression = 1.0
        self.flee_radius = 200.0
        self.perception_radius = 250.0

def test_hyper_command_python():
    w = MockWorld()
    c = CrowdSystem(w)

    b1 = MockBall("neural")
    b2 = MockBall("retaliator")

    c.process_external_command("user1", "!hyper aggression 2.5", [b1, b2])

    assert b1.aggression == 2.5
    assert b2.aggression == 1.0 # Only targets neural by default

    c.process_external_command("user2", "!hyper flee_radius 150.0 retaliator", [b1, b2])
    assert b1.flee_radius == 200.0
    assert b2.flee_radius == 150.0

    c.process_external_command("user3", "!hyper vision_radius 500.0 all", [b1, b2])
    assert b1.perception_radius == 500.0
    assert b2.perception_radius == 500.0

    # Check events
    cheers = [e for e in w.events if e[0] == "crowd_cheer"]
    assert len(cheers) == 3
    assert "aggression to 2.5" in cheers[0][1]["message"]
