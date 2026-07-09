import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=0, y=0, base_speed=2.0, hp=100, team="red", speed_boost_timer=0.0):
        self.x = x
        self.y = y
        self.base_speed = base_speed
        self.speed = base_speed
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.team = team
        self.speed_boost_timer = speed_boost_timer
        self.speed_overdrive_timer = 0.0
        self.time_warp_slow_timer = 0.0
        self._chrono_slow = 1.0
        self.slow_timer = 0.0
        self.frozen_timer = 0.0
        self.is_frozen = False
        self.stun_timer = 0.0

class MockItem:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.active = True

class MockWorld:
    def __init__(self, items):
        self.boosters = items
        self.arena = type('Arena', (), {'hazards': []})()

    def _collect_booster(self, ball, booster):
        pass

def test_speed_overdrive():
    # 1. Pick up speed booster
    item1 = MockItem("speed_booster_item", 5, 5)
    item2 = MockItem("speed_booster_item", 10, 10)
    world = MockWorld([item1, item2])

    ball = MockBall()
    action = Action(ball, world)
    action._idle = lambda d: None

    # Distance to item1 is ~7.07, perception radius is usually larger
    action._collect_booster(0.1)

    # Check if first pickup gave boost but no overdrive
    assert ball.speed_boost_timer > 0
    assert getattr(ball, "speed_overdrive_timer", 0.0) == 0.0

    # Manually move to item2
    ball.x = 10
    ball.y = 10
    action._collect_booster(0.1)

    # Second pickup while speed_boost_timer > 0 should grant overdrive
    assert getattr(ball, "speed_overdrive_timer", 0.0) > 0.0

    # Apply slow effects and execute frame
    ball.slow_timer = 5.0
    ball.frozen_timer = 5.0
    ball.is_frozen = True
    ball.time_warp_slow_timer = 5.0

    action.execute("idle", 0.1)

    # Verify immunities
    assert ball.slow_timer == 0.0
    assert ball.frozen_timer == 0.0
    assert not ball.is_frozen
    assert ball.time_warp_slow_timer == 0.0
    assert getattr(ball, "_chrono_slow", 1.0) == 1.0
