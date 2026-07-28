import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

@pytest.fixture
def cascading_stun_mode():
    mode = GAME_MODES["cascading_stun"]
    # Reset any state if necessary
    return mode

def test_cascading_stun_setup(cascading_stun_mode):
    world = MagicMock()
    b1 = MagicMock()
    b1.stun_arm_timer = 5.0
    b1.stun_timer = 5.0
    b2 = MagicMock()
    b2.stun_arm_timer = 0.0
    b2.stun_timer = 0.0
    b2.stun_arm_timer = 0.0
    b2.stun_arm_timer = 5.0
    b2.stun_timer = 5.0

    world.balls = [b1, b2]

    cascading_stun_mode.setup(world)

    assert b1.stun_arm_timer == 0.0
    assert b1.stun_timer == 0.0
    assert b2.stun_arm_timer == 0.0
    assert b2.stun_timer == 0.0

def test_cascading_stun_tick_collision_arms(cascading_stun_mode):
    world = MagicMock()
    b1 = MagicMock()
    b1.alive = True
    b1.x = 100.0
    b1.y = 100.0
    b1.radius = 20.0
    b1.stun_arm_timer = 0.0

    b2 = MagicMock()
    b2.stun_arm_timer = 0.0
    b2.stun_timer = 0.0
    b2.alive = True
    b2.x = 110.0
    b2.y = 110.0
    b2.radius = 20.0
    b2.stun_arm_timer = 0.0

    world.balls = [b1, b2]

    cascading_stun_mode.tick(world, 0.1)

    # Should be armed since they are close enough
    assert b1.stun_arm_timer == 2.0
    assert b2.stun_arm_timer == 2.0

def test_cascading_stun_tick_explosion(cascading_stun_mode):
    world = MagicMock()
    world.add_event = MagicMock()

    b1 = MagicMock()
    b1.alive = True
    b1.x = 100.0
    b1.y = 100.0
    b1.radius = 20.0
    b1.stun_arm_timer = 0.1
    # Place b2 far away for explosion test but close enough for blast radius? Explosion radius is 150.

    b2 = MagicMock()
    b2.stun_arm_timer = 0.0
    b2.stun_timer = 0.0
    b2.alive = True
    b2.x = 200.0
    b2.y = 200.0
    b2.radius = 20.0
    b2.stun_timer = 0.0

    b3 = MagicMock()
    b3.stun_arm_timer = 0.0
    b3.stun_timer = 0.0
    b3.stun_arm_timer = 0.0
    b3.alive = True
    b3.x = 1000.0 # far
    b3.y = 1000.0
    b3.radius = 20.0
    b3.stun_timer = 0.0

    world.balls = [b1, b2, b3]

    cascading_stun_mode.tick(world, 0.2)

    # b1 explodes, resets arm timer
    assert b1.stun_arm_timer == 0.0

    # b2 gets stunned
    assert b2.stun_timer == 1.5

    # b3 is far away, unaffected
    assert b3.stun_timer == 0.0
