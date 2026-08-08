from ai.game_modes import GAME_MODES
from system.test_crowd_system import MockBall

def test_invert_controls_mutator():
    mutator = GAME_MODES.get("invert_controls_mutator")
    assert mutator is not None

    b1 = MockBall(1, "team1", "player")
    b1.invert_timer = 0.0

    world = {}
    mutator.trigger_timer = 14.9
    mutator.apply_dynamic_traits(world, [b1], 0.2)

    assert b1.invert_timer >= 3.0

    mutator.apply_dynamic_traits(world, [b1], 1.0)
    assert b1.invert_timer == 3.0
    assert mutator.trigger_timer < 15.0
