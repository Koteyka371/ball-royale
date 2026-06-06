import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception

class MockEntity:
    def __init__(self, x=0, y=0, id=0):
        self.x = x
        self.y = y
        self.id = id

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

class MockBall:
    def __init__(self, x=0, y=0, radius=300):
        self.x = x
        self.y = y
        self.perception_radius = radius

def test_perception_scan_radius_filtering():
    ball = MockBall(0, 0, 100)
    world = MockWorld()

    # Inside radius
    e1 = MockEntity(50, 0)
    # Exactly on radius edge
    e2 = MockEntity(100, 0)
    # Outside radius
    e3 = MockEntity(101, 0)

    world.entities["enemies"] = [e1, e2, e3]

    perception = Perception(ball, world)
    data = perception.scan()

    assert len(data["enemies"]) == 2
    assert e1 in data["enemies"]
    assert e2 in data["enemies"]
    assert e3 not in data["enemies"]

def test_perception_levels():
    ball = MockBall(0, 0, 100)
    world = MockWorld()

    # Threat: 1.0 - (50/100) = 0.5 * 0.5 = 0.25
    e1 = MockEntity(50, 0)
    world.entities["enemies"] = [e1]

    # Threat: 1.0 - (0/100) = 1.0 * 0.8 = 0.8
    t1 = MockEntity(0, 0)
    world.entities["traps"] = [t1]

    # Opp: 1.0 - (20/100) = 0.8 * 0.5 = 0.4
    b1 = MockEntity(20, 0)
    world.entities["boosters"] = [b1]

    # Opp: 1.0 - (80/100) = 0.2 * 0.2 = 0.04
    a1 = MockEntity(80, 0)
    world.entities["allies"] = [a1]

    perception = Perception(ball, world)
    data = perception.scan()

    assert math.isclose(data["danger_level"], 1.05) # 0.25 + 0.8 = 1.05
    assert math.isclose(data["opportunity_level"], 0.44) # 0.4 + 0.04 = 0.44

def test_perception_fallback_levels():
    # If coordinate info isn't available, check the fallback code
    ball = MockBall(0, 0, 100)
    world = MockWorld()

    # Create entities without x, y
    class BasicEntity: pass

    world.entities["enemies"] = [BasicEntity(), BasicEntity()]
    world.entities["boosters"] = [BasicEntity()]

    perception = Perception(ball, world)
    data = perception.scan()

    # Fallback uses len(enemies) * 0.2 = 0.4
    assert math.isclose(data["danger_level"], 0.4)
    # Fallback uses len(boosters) * 0.3 = 0.3
    assert math.isclose(data["opportunity_level"], 0.3)
