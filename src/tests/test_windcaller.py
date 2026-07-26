import pytest
from ai.ball_types_windcaller import Windcaller

def test_windcaller_init():
    w = Windcaller(1)
    assert w.BALL_TYPE == "windcaller"
    assert w.gravity_well_immunity is True
    assert w.hazard_push_pull_immunity is True
    assert w.SKILL == "local_tornado"

def test_windcaller_skill():
    w = Windcaller(1)
    # Skill on cooldown initially since timer is 0
    assert w.use_skill() is True
    assert w.skill_timer == w.SKILL_COOLDOWN
    assert w.use_skill() is False
