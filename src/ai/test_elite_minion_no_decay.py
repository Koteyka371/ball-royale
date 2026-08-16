import pytest
from ai.action import Action
from ai.test_action_advanced import MockBall, MockWorld

def test_elite_minion_does_not_decay():
    world = MockWorld()

    minion = MockBall()
    minion.ball_type = "elite_minion"
    minion.is_elite_minion = True
    minion.is_minion = True
    minion.hp = 100.0
    minion.max_hp = 100.0
    minion.team = "undead"
    minion.x = 0
    minion.y = 0

    world.balls = [minion]

    action = Action(minion, world)
    action.execute(strategy={}, delta=1.0)

    assert minion.hp == 100.0
    assert getattr(minion, "alive", True)

def test_minion_decay():
    world = MockWorld()

    minion = MockBall()
    minion.ball_type = "minion"
    minion.is_elite_minion = False
    minion.is_minion = True
    minion.hp = 100.0
    minion.max_hp = 100.0
    minion.team = "undead"
    minion.x = 0
    minion.y = 0

    world.balls = [minion]

    action = Action(minion, world)
    action.execute(strategy={}, delta=1.0)

    assert minion.hp < 100.0
