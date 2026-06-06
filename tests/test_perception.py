import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception


class MockBall:
    def __init__(self, x=0.0, y=0.0, dmg=10.0, radius=300.0):
        self.x = x
        self.y = y
        self.DAMAGE = dmg
        self.PERCEPTION_RADIUS = radius


class MockWorld:
    def __init__(self):
        self.entities = {
            "enemies": [],
            "allies": [],
            "boosters": [],
        }

    def get_nearby_entities(self, ball, radius):
        return self.entities


def test_perception_initialization():
    ball = MockBall()
    world = MockWorld()
    perc = Perception(ball, world)
    assert perc.ball == ball
    assert perc.world == world


def test_distance_calculation():
    ball1 = MockBall(x=0, y=0)
    ball2 = MockBall(x=3, y=4)
    world = MockWorld()
    perc = Perception(ball1, world)
    dist = perc._calculate_distance(ball1, ball2)
    assert dist == 5.0


def test_scan_no_entities():
    ball = MockBall()
    world = MockWorld()
    perc = Perception(ball, world)
    data = perc.scan()
    assert len(data["enemies"]) == 0
    assert len(data["allies"]) == 0
    assert len(data["boosters"]) == 0
    assert data["danger_level"] == 0.0
    assert data["opportunity_level"] == 0.0
    assert data["closest_enemy_dist"] == float('inf')


def test_scan_with_enemies():
    ball = MockBall(x=0, y=0, radius=100.0)
    enemy1 = MockBall(x=50, y=0, dmg=20.0) # distance 50
    world = MockWorld()
    world.entities["enemies"] = [enemy1]
    perc = Perception(ball, world)
    data = perc.scan()

    assert len(data["enemies"]) == 1
    assert data["closest_enemy_dist"] == 50.0

    # Base threat for dist < radius is 0.2 + 0.2 * (1 - 50/100) = 0.3
    # Modified by damage (20.0 / 10.0) = 2.0 -> total threat = 0.6
    assert abs(data["danger_level"] - 0.6) < 0.001


def test_scan_with_allies_and_boosters():
    ball = MockBall(x=0, y=0, radius=100.0)
    ally1 = MockBall(x=0, y=50) # dist 50
    booster1 = MockBall(x=100, y=0) # dist 100
    mock_booster = 1 # simple mock

    world = MockWorld()
    world.entities["allies"] = [ally1]
    world.entities["boosters"] = [booster1, mock_booster]

    perc = Perception(ball, world)
    data = perc.scan()

    assert len(data["allies"]) == 1
    assert len(data["boosters"]) == 2
    assert data["closest_ally_dist"] == 50.0
    assert data["closest_booster_dist"] == 100.0

    # Ally opportunity: 0.1 + 0.1*(1 - 50/100) = 0.15
    # Booster1 opportunity: 0.3 (dist not < radius, so no bonus)
    # mock_booster opportunity: 0.3
    # Total opp = 0.75
    assert abs(data["opportunity_level"] - 0.75) < 0.001
