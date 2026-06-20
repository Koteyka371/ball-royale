import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_vampire import Vampire

def test_vampire_initialization():
    b = Vampire(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 80
    assert b.BALL_TYPE == "vampire"
    assert b.alive is True

def test_vampire_take_damage():
    b = Vampire(1)
    b.take_damage(40)
    assert b.hp == 40
    assert b.alive is True
    b.take_damage(80)
    assert b.hp <= 0
    assert b.alive is False
