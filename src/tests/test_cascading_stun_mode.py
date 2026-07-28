import pytest

from ai.game_modes import CascadingStunMode

def test_cascading_stun_mode_physics_and_dict():
    # Make sure we don't crash when passing dictionary objects as balls,
    # which can happen with standard hazards or mocked components.

    mode = CascadingStunMode()
    world = {"balls": [{"x": 0.0, "y": 0.0, "alive": True}, {"x": 500.0, "y": 500.0, "alive": True}]}

    mode.setup(world)

    assert world["balls"][0]["stun_arm_timer"] == 0.0
    assert world["balls"][0]["stun_timer"] == 0.0
    assert world["balls"][1]["stun_arm_timer"] == 0.0
    assert world["balls"][1]["stun_timer"] == 0.0

    # Tick loop to arm
    # Move them together
    world["balls"][0]["x"] = 100.0
    world["balls"][0]["y"] = 100.0
    world["balls"][0]["radius"] = 20.0

    world["balls"][1]["x"] = 100.0
    world["balls"][1]["y"] = 100.0
    world["balls"][1]["radius"] = 20.0

    mode.tick(world, 0.1)

    assert world["balls"][0]["stun_arm_timer"] == 2.0
    assert world["balls"][1]["stun_arm_timer"] == 2.0

    # Tick down the timer
    world["balls"][0]["stun_arm_timer"] = 0.1
    world["balls"][0]["x"] = 0.0
    world["balls"][1]["x"] = 1000.0
    mode.tick(world, 0.2)

    assert world["balls"][0]["stun_arm_timer"] == 0.0
    assert world["balls"][1]["stun_timer"] == 0.0
