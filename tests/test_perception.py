import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception

class MockEntity:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class MockBall:
    def __init__(self, x=0.0, y=0.0, perception_radius=300.0):
        self.x = x
        self.y = y
        self.perception_radius = perception_radius
        self.id = "main_ball"

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

def test_distance_calculation():
    ball = MockBall(0, 0)
    perception = Perception(ball, MockWorld())

    entity = MockEntity(1, 3, 4)
    # distance should be 5
    dist = perception._calculate_distance(ball, entity)
    assert math.isclose(dist, 5.0)

def test_scan_danger_and_opportunity():
    ball = MockBall(0, 0, perception_radius=100)
    world = MockWorld()

    # Add an enemy close by (distance 50)
    world.entities["enemies"] = [MockEntity(1, 50, 0)]

    # Add a booster far away but within radius (distance 80)
    world.entities["boosters"] = [MockEntity(2, 0, 80)]

    # Add a trap right on top of ball (distance 0)
    world.entities["traps"] = [MockEntity(3, 0, 0)]

    perception = Perception(ball, world)
    data = perception.scan()

    # Enemies danger = 0.5 * (1 - 50/100) = 0.25
    # Traps danger = 0.8 * (1 - 0/100) = 0.8
    # Total danger = 1.05 -> clamped to 1.0
    assert math.isclose(data["danger_level"], 1.0)

    # Boosters opportunity = 0.6 * (1 - 80/100) = 0.12
    assert math.isclose(data["opportunity_level"], 0.12)

    # Verify distance map
    assert data["distances"][1] == 50.0
    assert data["distances"][2] == 80.0
    assert data["distances"][3] == 0.0

def test_scan_outside_radius_ignored_for_score():
    ball = MockBall(0, 0, perception_radius=100)
    world = MockWorld()

    # Enemy just outside radius (distance 101)
    world.entities["enemies"] = [MockEntity(1, 101, 0)]

    perception = Perception(ball, world)
    data = perception.scan()

    # Outside radius, so doesn't contribute to danger score
    assert data["danger_level"] == 0.0
    # But distance is still recorded
    assert data["distances"][1] == 101.0
