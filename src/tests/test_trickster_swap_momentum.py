import pytest
from ai.action import Action
from ai.test_trickster_swap import MockWorld, MockBall, MockArena

def test_trickster_swap_momentum():
    trickster = MockBall(1, 100.0, 100.0, team="A")
    trickster.skill = "trickster_swap"
    trickster.SKILL = "trickster_swap"
    trickster.burn_timer = 5.0
    trickster.shield_timer = 2.0
    trickster.vx = 50.0
    trickster.vy = -30.0

    # Far decoy owned by trickster
    decoy = MockBall(3, 300.0, 300.0, team="A")
    decoy.is_decoy = True
    decoy.owner_id = trickster.id
    decoy.vx = 0.0
    decoy.vy = 0.0

    world = MockWorld([trickster, decoy])
    action = Action(trickster, world)

    # Run skill
    action._use_skill()

    # Trickster should swap with the decoy
    assert trickster.x == 300.0
    assert trickster.y == 300.0
    assert decoy.x == 100.0
    assert decoy.y == 100.0

    # Momentum transfer
    assert trickster.vx == 0.0
    assert trickster.vy == 0.0
    assert decoy.vx == 50.0
    assert decoy.vy == -30.0

    # Status transfer (ALL status including positive shield)
    assert trickster.burn_timer == 0.0
    assert getattr(trickster, "shield_timer", 0.0) == 0.0
    assert decoy.burn_timer == 5.0
    assert decoy.shield_timer == 2.0
