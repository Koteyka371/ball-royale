import pytest
from src.ai.action import Action
from src.ai.ball_types_gladiator import Gladiator

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "dummy"

class MockWorld:
    def __init__(self):
        self.balls = []

def test_gladiator_buffs_when_surrounded():
    gladiator = Gladiator(1, 0, 0)
    gladiator.team = 1
    gladiator.base_damage_multiplier = 1.0
    gladiator.damage_multiplier = 1.0

    world = MockWorld()
    world.balls = [
        gladiator,
        MockBall(2, 2, 10, 0),
        MockBall(3, 2, -10, 0)
    ]

    action = Action(gladiator, world)

    # Needs stubbing for chaser methods to not crash
    action._idle = lambda d: None
    action._chase = lambda d: None

    action.execute("idle", 0.1)

    assert gladiator.damage_multiplier == 2.0  # 1.0 + 0.5 * 2
    assert getattr(gladiator, "reflect_shield_active", False) == True
    assert getattr(gladiator, "reflect_shield_capacity", 0) == 40.0

def test_gladiator_no_buffs_when_alone():
    gladiator = Gladiator(1, 0, 0)
    gladiator.team = 1
    gladiator.base_damage_multiplier = 1.0
    gladiator.damage_multiplier = 1.0

    world = MockWorld()
    world.balls = [gladiator]

    action = Action(gladiator, world)
    action._idle = lambda d: None

    action.execute("idle", 0.1)

    assert gladiator.damage_multiplier == 1.0
    assert getattr(gladiator, "reflect_shield_active", False) == False
