import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_bard import Bard

def test_bard_initialization():
    b = Bard(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 85
    assert b.BALL_TYPE == "bard"
    assert b.alive is True

def test_bard_take_damage():
    b = Bard(1)
    b.take_damage(42)
    assert b.hp == 43
    assert b.alive is True
    b.take_damage(85)
    assert b.hp <= 0
    assert b.alive is False
