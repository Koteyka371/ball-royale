import pytest
import math
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

def test_dark_matter_void_mode():
    mode = GAME_MODES["dark_matter_void"]

    # Mock world
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'width': 1000.0, 'height': 1000.0})()

    # Mock balls
    b1 = type('MockBall', (), {'x': 500.0, 'y': 500.0, 'alive': True, 'hp': 100, 'base_speed': 100.0, 'speed': 100.0, 'skill_cooldown': 10.0})()
    b2 = type('MockBall', (), {'x': 500.0, 'y': 600.0, 'alive': True, 'hp': 100, 'base_speed': 100.0, 'speed': 100.0, 'skill_cooldown': 10.0})()
    b3 = type('MockBall', (), {'x': 900.0, 'y': 900.0, 'alive': True, 'hp': 100, 'base_speed': 100.0, 'speed': 100.0, 'skill_cooldown': 10.0})()

    balls = [b1, b2, b3]

    mode.setup(world, balls)
    assert mode.void_radius == 0.0

    # Tick loop to simulate void growth
    # Let's say we tick for 5 seconds (50 loops of 0.1s)
    # Void radius will be 50.0
    for _ in range(50):
        mode.tick(world, balls, 0.1)

    assert math.isclose(mode.void_radius, 50.0)

    # At this point:
    # b1 is at 500,500 (dist 0) - should be eliminated (hp == 0)
    assert b1.hp == 0

    # b2 is at 500,600 (dist 100). Void radius is 50, edge buffer is 150.
    # So 50 <= 100 < 200. b2 should have buff.
    # speed buff is 2.5 * base_speed
    # skill cooldown should decrease faster
    assert math.isclose(b2.speed, b2.base_speed * 2.5)
    assert b2.skill_cooldown < 10.0

    # b3 is at 900,900 (dist approx 565).
    # This is > 200. Should have normal speed.
    assert math.isclose(b3.speed, b3.base_speed)

    # Let's verify that a dead ball is not affected further
    b1_hp = b1.hp
    b1.speed = 0.0
    mode.tick(world, balls, 0.1)
    assert b1.hp == b1_hp
