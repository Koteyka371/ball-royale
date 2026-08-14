import pytest
from ai.action import Action
from ai.test_trickster_swap import MockWorld, MockBall, MockArena

def test_trickster_manual_swap():
    trickster = MockBall(1, 100.0, 100.0, team="A")
    trickster.skill = "trickster_swap"
    trickster.SKILL = "trickster_swap"

    # We want to swap with the closer decoy because we manually selected it
    # to prove it isn't just taking the furthest one like before.
    decoy_close = MockBall(2, 200.0, 200.0, team="A")
    decoy_close.is_decoy = True
    decoy_close.owner_id = trickster.id

    decoy_far = MockBall(3, 500.0, 500.0, team="A")
    decoy_far.is_decoy = True
    decoy_far.owner_id = trickster.id

    trickster.trickster_swap_target_id = decoy_close.id

    world = MockWorld([trickster, decoy_close, decoy_far])
    action = Action(trickster, world)

    action._use_skill()

    # Should swap with decoy_close
    assert trickster.x == 200.0
    assert trickster.y == 200.0
    assert decoy_close.x == 100.0
    assert decoy_close.y == 100.0
    assert decoy_far.x == 500.0
    assert decoy_far.y == 500.0

def test_trickster_manual_swap_invalid_target():
    trickster = MockBall(1, 100.0, 100.0, team="A")
    trickster.skill = "trickster_swap"
    trickster.SKILL = "trickster_swap"

    decoy_close = MockBall(2, 200.0, 200.0, team="A")
    decoy_close.is_decoy = True
    decoy_close.owner_id = trickster.id

    decoy_far = MockBall(3, 500.0, 500.0, team="A")
    decoy_far.is_decoy = True
    decoy_far.owner_id = trickster.id

    # Invalid ID
    trickster.trickster_swap_target_id = 999

    world = MockWorld([trickster, decoy_close, decoy_far])
    action = Action(trickster, world)

    action._use_skill()

    # Should fall back to furthest decoy (decoy_far)
    assert trickster.x == 500.0
    assert trickster.y == 500.0
    assert decoy_far.x == 100.0
    assert decoy_far.y == 100.0
    assert decoy_close.x == 200.0
    assert decoy_close.y == 200.0
