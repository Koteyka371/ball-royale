import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.perception import Perception


class MockEntity:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


class MockWorldEntities:
    def __init__(self, enemies, allies, boosters, traps):
        self.entities = {
            "enemies": enemies,
            "allies": allies,
            "boosters": boosters,
            "traps": traps,
        }


def test_perception_scan_distances():
    ball = MockEntity("b1", 100, 100)
    ball.perception_radius = 500

    enemy1 = MockEntity("e1", 150, 100)  # dist: 50
    enemy2 = MockEntity("e2", 120, 100)  # dist: 20
    enemy3 = MockEntity("e3", 200, 100)  # dist: 100

    booster1 = MockEntity("bo1", 100, 110) # dist: 10
    booster2 = MockEntity("bo2", 100, 130) # dist: 30

    ally1 = MockEntity("a1", 10, 10)

    world = MockWorldEntities([enemy1, enemy2, enemy3], [ally1], [booster1, booster2], [])

    perception = Perception(ball, world)
    data = perception.scan()

    assert len(data["enemies"]) == 3
    assert len(data["boosters"]) == 2
    assert len(data["allies"]) == 1

    assert data["nearest_enemy"] == enemy2
    assert data["nearest_booster"] == booster1
    assert data["nearest_ally"] == ally1

    assert data["danger_level"] == 3 * 0.2
    assert data["opportunity_level"] == 2 * 0.3 + 1 * 0.1
