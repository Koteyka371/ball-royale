import pytest
from tests.test_action import MockWorld, MockBall
from ai.action import Action

def test_trickster_clone_skill():
    owner = MockBall(x=10, y=10)
    owner.id = 111
    owner.team = "owner_team"
    owner.ball_type = "trickster"
    owner.skill = "trickster_clone"
    owner.skill_timer = 0.0
    owner.max_hp = 100

    world = MockWorld()
    world.balls = [owner]
    action = Action(owner, world)

    action._use_skill()

    assert len(world.balls) == 2

    clone = world.balls[1]
    assert getattr(clone, "damage", None) == 0.0
    assert getattr(clone, "is_decoy_clone", False) is True
    assert getattr(clone, "is_illusion", False) is True
    assert getattr(clone, "is_confetti_clone", False) is True
    assert getattr(clone, "mimic_owner", None) == owner.id
