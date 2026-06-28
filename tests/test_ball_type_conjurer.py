import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ai.ball_types_conjurer import Conjurer
from ai.action import Action
import random

def test_conjurer_initialization():
    conjurer = Conjurer(1, 10.0, 20.0)
    assert conjurer.id == 1
    assert conjurer.x == 10.0
    assert conjurer.y == 20.0
    assert conjurer.hp == Conjurer.HP
    assert conjurer.BALL_TYPE == "conjurer"
    assert conjurer.SKILL == "summon_minions"

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.dead_balls = []
        self.next_id = 1000
        self.tick = 1
        self.arena = MockArena()

def test_conjurer_skill_summons_minions():
    conjurer = Conjurer(1, 0.0, 0.0)
    conjurer.skill_timer = 0
    conjurer.current_action = "use_skill"
    world = MockWorld()
    world.balls.append(conjurer)

    action = Action(conjurer, world)
    action.execute(conjurer.current_action, 1.0)

    # Check if we have more balls (minions)
    assert len(world.balls) > 1

    minions = [b for b in world.balls if getattr(b, "is_minion", False)]
    assert len(minions) >= 2 and len(minions) <= 4

    for m in minions:
        assert m.minion_owner == conjurer.id
        assert m.hp == 20
        assert m.max_hp == 20
        assert m.team == conjurer.BALL_TYPE
