import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_monk import Monk

def test_monk_initialization():
    b = Monk(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 110
    assert b.BALL_TYPE == "monk"
    assert b.alive is True

def test_monk_take_damage():
    b = Monk(1)
    b.take_damage(55)
    assert b.hp == 55
    assert b.alive is True
    b.take_damage(110)
    assert b.hp <= 0
    assert b.alive is False
