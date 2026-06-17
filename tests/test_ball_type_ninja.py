import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_ninja import Ninja

def test_ninja_initialization():
    ball = Ninja(ball_id=1, x=10.0, y=20.0)

    assert ball.id == 1
    assert ball.x == 10.0
    assert ball.y == 20.0

    assert ball.BALL_TYPE == "ninja"
    assert ball.hp == 65.0
    assert ball.max_hp == 65.0
    assert ball.SPEED == 4.5
    assert ball.DAMAGE == 25
    assert ball.RADIUS == 8
    assert ball.PERCEPTION_RADIUS == 350
    assert ball.AGGRESSION == 0.8
    assert ball.COLOR == "black"
    assert ball.SKILL == "stealth"
    assert ball.SKILL_COOLDOWN == 4.0

    assert ball.alive is True
    assert ball.kills == 0
    assert ball.first_hit_taken is False
    assert ball.current_action == "idle"
    assert ball.skill_timer == 0.0
    assert ball.personality.character == "cunning"

def test_ninja_hp_percent():
    ball = Ninja(ball_id=2)
    assert ball.get_hp_percent() == 1.0

    ball.take_damage(32.5)
    assert ball.get_hp_percent() == 0.5
    assert ball.first_hit_taken is True

def test_ninja_take_damage_death():
    ball = Ninja(ball_id=3)
    ball.take_damage(65.0)
    assert ball.hp <= 0
    assert ball.alive is False

def test_ninja_actions():
    ball = Ninja(ball_id=4)

    ball.flee(0.1)
    assert ball.current_action == "flee"

    ball.attack(0.1)
    assert ball.current_action == "attack"

    ball.defend(0.1)
    assert ball.current_action == "defend"

    ball.collect_booster(0.1)
    assert ball.current_action == "opportunistic"

    ball.idle(0.1)
    assert ball.current_action == "idle"

def test_ninja_use_skill():
    ball = Ninja(ball_id=5)

    # Should use skill initially
    assert ball.use_skill() is True
    assert ball.skill_timer == ball.SKILL_COOLDOWN

    # Shouldn't use skill on cooldown
    assert ball.use_skill() is False

def test_ninja_repr():
    ball = Ninja(ball_id=6)
    repr_str = repr(ball)
    assert "ninja#6" in repr_str
    assert "HP=65.0/65.0" in repr_str
    assert "[idle]" in repr_str
