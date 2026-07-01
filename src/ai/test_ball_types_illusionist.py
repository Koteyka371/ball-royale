import pytest
from ai.ball_types_illusionist import Illusionist

def test_illusionist_initialization():
    ball = Illusionist(1, x=10.0, y=20.0)
    assert ball.BALL_TYPE == "illusionist"
    assert ball.SKILL == "mimic_clone"
    assert ball.hp == 75
    assert ball.SPEED == 3.5
    assert ball.DAMAGE == 12

def test_illusionist_use_skill():
    ball = Illusionist(1, x=10.0, y=20.0)

    # Initial state
    assert ball.skill_timer == 0.0

    # Should use skill successfully
    assert ball.use_skill() is True
    assert ball.skill_timer == 6.0

    # Should fail if cooldown is active
    assert ball.use_skill() is False

def test_illusionist_take_damage():
    ball = Illusionist(1, x=10.0, y=20.0)
    ball.take_damage(25)
    assert ball.hp == 50
    assert ball.first_hit_taken is True

    ball.take_damage(50)
    assert ball.hp == 0
    assert ball.alive is False
