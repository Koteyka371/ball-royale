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
    world.entities["allies"] = [MockEntity("a1", -20, 0)]

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

def test_perception_radius_by_ball_type():
    from ai.ball_types_assassin import Assassin
    from ai.ball_types_sniper import Sniper
    from ai.perception import Perception

    assassin_ball = Assassin(1, 0, 0)
    sniper_ball = Sniper(2, 0, 0)

    assert assassin_ball.perception_radius == 300
    assert sniper_ball.perception_radius == 500

    world = MockWorld()

    # Sniper sees an enemy at 400 distance
    world.entities["enemies"] = [MockEntity("e1", 400, 0)]

    sniper_perception = Perception(sniper_ball, world)
    sniper_data = sniper_perception.scan()
    assert "e1" in sniper_data["distances"]
    assert sniper_data["threat_level"] > 0

    assassin_perception = Perception(assassin_ball, world)
    assassin_data = assassin_perception.scan()
    # Wait, in our mock world it just returns whatever is in world.entities
    # but the perception system uses max(0, 1 - dist/radius)
    # Let's check threat level calculations
    assert "e1" in assassin_data["distances"]
    # The enemy is at 400, but assassin's radius is 300
    # max(0, 1 - 400/300) = 0
    assert assassin_data["threat_level"] == 0.0
