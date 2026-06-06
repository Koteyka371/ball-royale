import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception

class MockPosition:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        import math
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class MockEntity:
    def __init__(self, x, y):
        self.position = MockPosition(x, y)

class MockBall(MockEntity):
    def __init__(self, x=0, y=0, perception_radius=300.0):
        super().__init__(x, y)
        self.perception_radius = perception_radius

class MockWorld:
    def __init__(self):
        self.entities = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": []
        }
        self.last_radius_checked = 0

    def get_nearby_entities(self, ball, radius):
        self.last_radius_checked = radius
        # Only return entities within radius to simulate world filtering
        filtered = {
            "enemies": [e for e in self.entities["enemies"] if ball.position.distance_to(e.position) <= radius],
            "allies": [e for e in self.entities["allies"] if ball.position.distance_to(e.position) <= radius],
            "boosters": [e for e in self.entities["boosters"] if ball.position.distance_to(e.position) <= radius],
            "traps": [e for e in self.entities["traps"] if ball.position.distance_to(e.position) <= radius],
        }
        return filtered

def test_perception_initialization():
    ball = MockBall()
    world = MockWorld()
    perception = Perception(ball, world)

    assert perception.ball == ball
    assert perception.world == world

def test_perception_scan_radius():
    ball = MockBall(perception_radius=150.0)
    world = MockWorld()
    perception = Perception(ball, world)

    perception.scan()
    assert world.last_radius_checked == 150.0

def test_perception_distances_and_threats():
    ball = MockBall(0, 0)
    world = MockWorld()

    enemy1 = MockEntity(30, 40) # distance 50
    enemy2 = MockEntity(0, 100) # distance 100
    trap1 = MockEntity(0, 10) # distance 10

    world.entities["enemies"] = [enemy1, enemy2]
    world.entities["traps"] = [trap1]

    perception = Perception(ball, world)
    data = perception.scan()

    # Check distances
    assert data["distances"][id(enemy1)] == 50.0
    assert data["distances"][id(enemy2)] == 100.0
    assert data["distances"][id(trap1)] == 10.0

    # Check threats
    # enemy1: 0.2 + 100/50 = 2.2
    # enemy2: 0.2 + 100/100 = 1.2
    # trap1: 0.5 + 50/10 = 5.5
    # total danger: 2.2 + 1.2 + 5.5 = 8.9
    assert abs(data["danger_level"] - 8.9) < 0.001

def test_perception_opportunities():
    ball = MockBall(0, 0)
    world = MockWorld()

    booster1 = MockEntity(0, 25) # distance 25
    ally1 = MockEntity(0, 50) # distance 50

    world.entities["boosters"] = [booster1]
    world.entities["allies"] = [ally1]

    perception = Perception(ball, world)
    data = perception.scan()

    # Check distances
    assert data["distances"][id(booster1)] == 25.0
    assert data["distances"][id(ally1)] == 50.0

    # Check opportunity
    # booster1: 0.3 + 100/25 = 4.3
    # ally1: 0.1
    # total: 4.4
    assert abs(data["opportunity_level"] - 4.4) < 0.001
