import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_druid import Druid

def test_druid_initialization():
    b = Druid(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 130
    assert b.BALL_TYPE == "druid"
    assert b.alive is True

def test_druid_take_damage():
    b = Druid(1)
    b.take_damage(65)
    assert b.hp == 65
    assert b.alive is True
    b.take_damage(130)
    assert b.hp <= 0
    assert b.alive is False
