import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_mage import Mage

def test_mage_initialization():
    b = Mage(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 60
    assert b.BALL_TYPE == "mage"
    assert b.alive is True

def test_mage_take_damage():
    b = Mage(1)
    b.take_damage(30)
    assert b.hp == 30
    assert b.alive is True
    b.take_damage(60)
    assert b.hp <= 0
    assert b.alive is False
