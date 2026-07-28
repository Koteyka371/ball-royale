import pytest
from ai.action import Action
from ai.test_trickster_swap import MockWorld, MockBall, MockArena

def test_mimic_clone_swap():
    trickster = MockBall(1, 100.0, 100.0, team="A")
    trickster.skill = "mimic_clone"
    trickster.SKILL_COOLDOWN = 5.0
    trickster.burn_timer = 5.0
    trickster.shield_timer = 2.0
    trickster.vx = 50.0
    trickster.vy = -30.0
    trickster.is_stunned = False

    # Mimic clone owned by trickster
    clone = MockBall(3, 300.0, 300.0, team="A")
    clone.is_mimic_clone = True
    clone.mimic_owner = trickster.id
    clone.vx = 0.0
    clone.vy = 0.0

    world = MockWorld([trickster, clone])
    action = Action(trickster, world)

    # Run skill
    action._use_skill()

    # Trickster should swap with the clone
    assert trickster.x == 300.0
    assert trickster.y == 300.0
    assert clone.x == 100.0
    assert clone.y == 100.0

    # Momentum transfer
    assert trickster.vx == 0.0
    assert trickster.vy == 0.0
    assert clone.vx == 50.0
    assert clone.vy == -30.0

    # Status transfer (ALL status including positive shield)
    assert trickster.burn_timer == 0.0
    assert getattr(trickster, "shield_timer", 0.0) == 0.0
    assert clone.burn_timer == 5.0
    assert getattr(clone, "shield_timer", 0.0) == 2.0

    # Has swapped flag set
    assert getattr(clone, "has_swapped", False) == True
