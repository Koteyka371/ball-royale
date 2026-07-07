import pytest
from ai.action import Action
from ai.perception import Perception
from unittest.mock import MagicMock

class FakeHazard:
    def __init__(self, id, x, y, radius, kind):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.kind = kind
        self.active = True

class FakeBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.speed = 10.0
        self.base_speed = 10.0
        self.radius = 15.0
        self.ball_type = "basic"
        self.stealth_booster_timer = 0.0

    def has_method(self, method_name):
        return False

    def get_hp_percent(self):
        return self.hp / self.max_hp

class FakeArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0
        self.is_sandstorming = False

    def is_point_inside(self, x, y, r=0):
        return True

class FakeWorld:
    def __init__(self):
        self.arena = FakeArena()
        self.balls = []
        self.boosters = []
        self.time = 0.0

    def add_event(self, type, data):
        pass

def test_stealth_booster_collection_and_timer():
    world = FakeWorld()
    ball = FakeBall(1, 100.0, 100.0)
    world.balls.append(ball)

    # Just set the timer directly to test action decrement
    ball.stealth_booster_timer = 15.0
    action = Action(ball, world)

    action.execute("idle", 1.0)

    assert ball.stealth_booster_timer == 14.0, "Timer should decrement by delta"

def test_stealth_booster_perception():
    # Setup mock get_nearby_entities
    def mock_get_nearby_entities(self_obj, ball, radius):
        return entities
    FakeWorld.get_nearby_entities = mock_get_nearby_entities
    world = FakeWorld()
    spotter = FakeBall(1, 100.0, 100.0)
    spotter.team = "A"

    enemy = FakeBall(2, 150.0, 100.0)
    enemy.team = "B"
    # Enemy is normally visible (distance 50)

    world.balls.append(spotter)
    world.balls.append(enemy)

    entities = {
        "enemies": [enemy],
        "allies": [spotter]
    }

    # Normally visible
    perception = Perception(spotter, world)
    data = perception.scan()
    assert len(data["enemies"]) == 1, "Enemy should be visible without stealth booster"

    # Activate stealth booster on enemy
    enemy.stealth_booster_timer = 10.0

    # Now they should be invisible since distance is > 10
    data_stealthed = perception.scan()
    assert len(data_stealthed["enemies"]) == 0, "Enemy should be invisible with stealth booster"

    # Move enemy right next to spotter (distance < 10)
    enemy.x = 105.0
    data_close = perception.scan()
    assert len(data_close["enemies"]) == 1, "Stealthed enemy should be visible if very close"

if __name__ == "__main__":
    test_stealth_booster_collection_and_timer()
    test_stealth_booster_perception()
    print("All stealth booster tests passed!")
