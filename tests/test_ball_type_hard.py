import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_hard import Hard

def test_hard_initialization():
    hard = Hard(ball_id=1, x=10, y=20)
    assert hard.BALL_TYPE == "hard"
    assert hard.id == 1
    assert hard.x == 10
    assert hard.y == 20
    assert hard.hp == hard.HP
    assert hard.max_hp == hard.HP
    assert hard.difficulty == "hard"

def test_hard_actions():
    hard = Hard(ball_id=1)
    hard.flee(0.1)
    assert hard.current_action == "flee"
    hard.attack(0.1)
    assert hard.current_action == "attack"
    hard.defend(0.1)
    assert hard.current_action == "defend"
    hard.collect_booster(0.1)
    assert hard.current_action == "collect_booster"
    hard.idle(0.1)
    assert hard.current_action == "idle"

def test_hard_take_damage():
    hard = Hard(ball_id=1)
    initial_hp = hard.hp
    hard.take_damage(10)
    assert hard.first_hit_taken is True
    assert hard.hp == initial_hp - 10
    assert hard.alive is True

    hard.take_damage(hard.HP)
    assert hard.hp <= 0
    assert hard.alive is False

def test_hard_use_skill():
    hard = Hard(ball_id=1)
    assert hard.skill_timer == 0.0
    used = hard.use_skill()
    assert used is True
    assert hard.skill_timer == hard.SKILL_COOLDOWN

    used_again = hard.use_skill()
    assert used_again is False

def test_hard_hp_percent():
    hard = Hard(ball_id=1)
    assert hard.get_hp_percent() == 1.0
    hard.hp = hard.max_hp / 2
    assert hard.get_hp_percent() == 0.5
