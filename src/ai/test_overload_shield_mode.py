import pytest
import math
from ai.game_modes import OverloadShieldMode

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.reflect_shield_active = False
        self.reflect_shield_capacity = 0.0
        self.stamina = 100.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_overload_shield_capacity_boost():
    mode = OverloadShieldMode()
    world = MockWorld()
    ball = MockBall(1, 0, 0)

    # Shield inactive initially
    mode.tick(world, [ball], 0.016)
    assert getattr(ball, "overload_shield_boosted", False) == False

    # Activate shield with 50 capacity
    ball.reflect_shield_active = True
    ball.reflect_shield_capacity = 50.0

    mode.tick(world, [ball], 0.016)

    # Shield capacity should be boosted to 150 (300%)
    assert getattr(ball, "overload_shield_boosted", False) == True
    assert ball.reflect_shield_capacity == 150.0

    # Explosion attributes should be doubled
    assert getattr(ball, "reflect_explosion_radius") == 300.0
    assert getattr(ball, "reflect_explosion_damage") == 100.0

    # Next tick it shouldn't boost again
    mode.tick(world, [ball], 0.016)
    assert ball.reflect_shield_capacity == 150.0

def test_overload_shield_stamina_drain():
    mode = OverloadShieldMode()
    world = MockWorld()
    ball = MockBall(1, 0, 0)

    ball.reflect_shield_active = True
    ball.reflect_shield_capacity = 50.0

    mode.tick(world, [ball], 1.0) # 1 second

    # Drain rate is 10 per second
    assert getattr(ball, "overload_shield_boosted", False) == True
    assert ball.stamina == 90.0

    # Should not drain below 0
    mode.tick(world, [ball], 10.0)
    assert ball.stamina == 0.0

def test_overload_shield_break_explosion():
    mode = OverloadShieldMode()
    world = MockWorld()
    ball = MockBall(1, 100, 100)

    ball.reflect_shield_active = True
    ball.reflect_shield_capacity = 50.0

    mode.tick(world, [ball], 0.016)

    assert getattr(ball, "overload_shield_boosted", False) == True
    assert getattr(ball, "reflect_explosion_radius") == 300.0

    # Simulate shield breaking
    ball.reflect_shield_active = False
    ball.reflect_shield_capacity = 0.0

    mode.tick(world, [ball], 0.016)

    # Should revert explosion attributes
    assert getattr(ball, "overload_shield_boosted", False) == False
    assert getattr(ball, "reflect_explosion_radius") == 150.0
    assert getattr(ball, "reflect_explosion_damage") == 50.0
