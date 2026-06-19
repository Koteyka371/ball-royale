import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_neural import Neural

def test_neural_initialization():
    neural = Neural(1, x=10.0, y=20.0)
    assert neural.id == 1
    assert neural.x == 10.0
    assert neural.y == 20.0
    assert neural.BALL_TYPE == "neural"
    assert neural.hp == neural.max_hp
    assert neural.hp == 100
    assert neural.skill_timer == 0.0
    assert neural.SKILL == "numpy"

    assert neural.use_skill() is True
    assert neural.skill_timer == 4.0
    assert neural.current_action in ["attack", "flee", "idle"]

    neural.take_damage(20)
    assert neural.hp == 80
    assert neural.first_hit_taken is True
