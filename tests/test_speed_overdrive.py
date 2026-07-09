import pytest
from ai.action import Action
from unittest.mock import MagicMock

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.entities = []
        self.balls = []

    def add_event(self, event_type, data=None):
        pass

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.kind = kind
        self.radius = 10.0
        self.alive = True
        self.speed = 2.0
        self.base_speed = 2.0

def test_speed_overdrive():
    world = MockWorld()
    ball = MockEntity(1, 0, 0)
    world.balls = [ball]
    world.entities = [ball]
    action = Action(1, world)
    action.ball = ball

    # First booster
    booster1 = MockEntity(2, 0, 0, kind="speed_booster_item")
    world.boosters = [booster1]
    world.arena.hazards = [booster1]

    # Needs to mock _get_boosters to return booster1
    action._get_boosters = lambda: world.boosters

    action._collect_booster(0.1)

    assert ball.speed_boost_timer == 5.0
    assert not getattr(ball, "speed_overdrive", False)

    # Second booster
    booster2 = MockEntity(3, 0, 0, kind="speed_booster_item")
    world.boosters = [booster2]
    world.arena.hazards = [booster2]
    action._get_boosters = lambda: world.boosters

    action._collect_booster(0.1)

    assert ball.speed_boost_timer == 5.0
    assert getattr(ball, "speed_overdrive", False)

    # Apply slow and freeze
    ball.slow_timer = 5.0
    ball.stun_timer = 5.0
    ball.frozen_timer = 5.0
    ball.is_stunned = True

    # Tick loop to see if immune
    action.execute("idle", 0.1)

    assert ball.slow_timer == 0.0
    assert ball.stun_timer == 0.0
    assert ball.frozen_timer == 0.0
    assert not getattr(ball, "is_stunned", False)

    # Test expiry
    ball.speed_boost_timer = 0.01
    action.execute("idle", 0.1)

    assert ball.speed_boost_timer == 0.0
    assert not getattr(ball, "speed_overdrive", False)
