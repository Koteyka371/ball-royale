import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception

class MockEntity:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class MockAlly(MockEntity):
    def __init__(self, id, x, y, team_message=""):
        super().__init__(id, x, y)
        self.team_message = team_message

class MockWorld:
    def __init__(self):
        self.entities = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": []
        }

    def get_nearby_entities(self, ball, radius):
        return self.entities

def test_perception_initialization():
    ball = MockEntity("ball_1", 0, 0)
    world = MockWorld()
    perception = Perception(ball, world)

    assert perception.ball == ball
    assert perception.world == world

def test_perception_scan_distances_and_scores():
    ball = MockEntity("hero", 0, 0)
    setattr(ball, "perception_radius", 100.0)

    world = MockWorld()
    # Distance 50 (0.5 max)
    world.entities["enemies"] = [MockEntity("e1", 30, 40)]
    # Distance 10 (0.9 max)
    world.entities["traps"] = [MockEntity("t1", 0, 10)]
    # Distance 80 (0.2 max)
    world.entities["boosters"] = [MockEntity("b1", 80, 0)]
    # Distance 20 (0.8 max)
    world.entities["allies"] = [MockAlly("a1", -20, 0, team_message="help")]

    perception = Perception(ball, world)
    data = perception.scan()

    assert data["distances"]["e1"] == 50.0
    assert data["distances"]["t1"] == 10.0
    assert data["distances"]["b1"] == 80.0
    assert data["distances"]["a1"] == 20.0

    # Threat logic:
    # enemy: max(0, 1 - 50/100) * 1.5 = 0.5 * 1.5 = 0.75
    # trap: max(0, 1 - 10/100) * 2.0 = 0.9 * 2.0 = 1.8
    # Total threat: 2.55
    assert abs(data["threat_level"] - 2.55) < 0.001

    # Opportunity logic:
    # booster: max(0, 1 - 80/100) * 1.0 = 0.2 * 1.0 = 0.2
    # ally: max(0, 1 - 20/100) * 0.5 = 0.8 * 0.5 = 0.4
    # Total opp: 0.6
    assert abs(data["opportunity_score"] - 0.6) < 0.001

    assert data["team_messages"] == ["help"]

    # Backward compatibility
    assert data["danger_level"] == 0.2
    assert data["opportunity_level"] == 0.4

def test_perception_empty_world():
    ball = MockEntity("hero", 0, 0)
    world = MockWorld()
    perception = Perception(ball, world)
    data = perception.scan()

    assert data["threat_level"] == 0.0
    assert data["opportunity_score"] == 0.0
    assert data["danger_level"] == 0.0
    assert data["opportunity_level"] == 0.0
    assert not data["enemies"]
    assert not data["allies"]
    assert not data["boosters"]
    assert not data["traps"]
