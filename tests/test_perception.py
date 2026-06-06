import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception

class MockPosition:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockBall:
    def __init__(self, x=0, y=0, radius=None):
        self.position = MockPosition(x, y)
        if radius is not None:
            self.perception_radius = radius

class MockWorld:
    def __init__(self):
        self.entities = {
            "enemies": [],
            "allies": [],
            "boosters": [],
        }

    def get_nearby_entities(self, ball, radius):
        return self.entities

def test_perception_radius():
    world = MockWorld()

    # Test default
    ball1 = MockBall()
    p1 = Perception(ball1, world)
    assert p1.get_perception_radius() == 300.0

    # Test custom
    ball2 = MockBall(radius=500.0)
    p2 = Perception(ball2, world)
    assert p2.get_perception_radius() == 500.0

def test_perception_scan_distances():
    ball = MockBall(0, 0, 100.0) # perception radius 100
    world = MockWorld()

    # Place an enemy at 50 units away (half of radius)
    # The math for danger is 1.0 * (1.0 - min(dist/radius, 1.0))
    # dist = 50, radius = 100 => 1.0 - 0.5 = 0.5
    enemy1 = MockBall(50, 0)
    world.entities["enemies"].append(enemy1)

    p = Perception(ball, world)
    data = p.scan()

    assert data["danger_level"] == 0.5

    # Place a booster at 0 units away (on top)
    # The math for opportunity is 1.5 * (1.0 - min(dist/radius, 1.0))
    # dist = 0, radius = 100 => 1.0 - 0 = 1.0.  1.0 * 1.5 = 1.5
    booster1 = MockBall(0, 0)
    world.entities["boosters"].append(booster1)

    data2 = p.scan()
    assert data2["danger_level"] == 0.5
    assert data2["opportunity_level"] == 1.5

def test_perception_scan_fallback():
    # Test when objects don't have positions
    class NoPosBall:
        pass

    ball = NoPosBall()
    world = MockWorld()
    world.entities["enemies"].append(NoPosBall())
    world.entities["enemies"].append(NoPosBall())
    world.entities["boosters"].append(NoPosBall())

    p = Perception(ball, world)
    data = p.scan()

    # Fallback math: danger = len * 0.2 = 0.4
    assert data["danger_level"] == 0.4
    # Fallback math: opp = len * 0.3 = 0.3
    assert data["opportunity_level"] == 0.3
