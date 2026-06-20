import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_paladin import Paladin

def test_paladin_initialization():
    b = Paladin(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 180
    assert b.BALL_TYPE == "paladin"
    assert b.alive is True

def test_paladin_take_damage():
    b = Paladin(1)
    b.take_damage(90)
    assert b.hp == 90
    assert b.alive is True
    b.take_damage(180)
    assert b.hp <= 0
    assert b.alive is False
