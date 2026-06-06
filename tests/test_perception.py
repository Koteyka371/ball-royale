import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception

class MockBall:
    def __init__(self, x=0, y=0, perception_radius=300):
        self.x = x
        self.y = y
        self.perception_radius = perception_radius

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
    ball = MockBall()
    world = MockWorld()
    perception = Perception(ball, world)

    assert perception.ball == ball
    assert perception.world == world

def test_scan_identifies_entities():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    e1 = MockBall(x=10, y=0)
    e2 = MockBall(x=20, y=0)
    a1 = MockBall(x=0, y=30)
    b1 = MockBall(x=0, y=40)
    t1 = MockBall(x=5, y=0)

    world.entities["enemies"] = [e2, e1] # Add out of order to test sorting
    world.entities["allies"] = [a1]
    world.entities["boosters"] = [b1]
    world.entities["traps"] = [t1]

    perception = Perception(ball, world)
    data = perception.scan()

    assert len(data["enemies"]) == 2
    assert len(data["allies"]) == 1
    assert len(data["boosters"]) == 1
    assert len(data["traps"]) == 1

    # Check sorting (closest first)
    assert data["enemies"][0]["entity"] == e1
    assert data["enemies"][1]["entity"] == e2

def test_distance_and_threat_calculation():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    # Enemy at distance 100 -> danger should be 50/100 = 0.5
    world.entities["enemies"] = [MockBall(x=100, y=0)]

    # Trap at distance 25 -> danger should be min(1.0, 50/25=2.0) = 1.0
    world.entities["traps"] = [MockBall(x=25, y=0)]

    perception = Perception(ball, world)
    data = perception.scan()

    # Total danger = 0.5 + 1.0 = 1.5
    assert data["danger_level"] == 1.5

    # Booster at distance 50 -> opportunity should be min(1.0, 100/50=2.0) = 1.0
    world.entities["boosters"] = [MockBall(x=0, y=50)]

    # 2 Allies -> opportunity + 0.2
    world.entities["allies"] = [MockBall(), MockBall()]

    data = perception.scan()
    # Total opportunity = 1.0 + 0.2 = 1.2
    assert data["opportunity_level"] == 1.2
