import pytest
from ai.action import Action
from ai.test_trickster_swap import MockWorld, MockBall, MockArena

def test_trickster_swap_resonance():
    trickster = MockBall(1, 100.0, 100.0, team="A")
    trickster.skill = "trickster_swap"
    trickster.SKILL = "trickster_swap"

    # Far decoy owned by trickster
    decoy = MockBall(3, 300.0, 300.0, team="A")
    decoy.is_decoy = True
    decoy.owner_id = trickster.id

    # Enemy near trickster origin
    enemy_origin = MockBall(4, 110.0, 110.0, team="B")
    enemy_origin.slow_timer = 0.0

    # Enemy near decoy destination
    enemy_dest = MockBall(5, 310.0, 310.0, team="B")
    enemy_dest.slow_timer = 0.0

    # Enemy far away
    enemy_far = MockBall(6, 500.0, 500.0, team="B")
    enemy_far.slow_timer = 0.0

    world = MockWorld([trickster, decoy, enemy_origin, enemy_dest, enemy_far])
    action = Action(trickster, world)

    # Run skill
    action._use_skill()

    # Trickster should swap with the decoy
    assert trickster.x == 300.0
    assert trickster.y == 300.0

    # Enemies near origin and destination should be slowed
    assert enemy_origin.slow_timer > 0.0
    assert enemy_dest.slow_timer > 0.0

    # Far enemy should not be slowed
    assert enemy_far.slow_timer == 0.0
