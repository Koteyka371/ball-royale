import pytest # type: ignore
from ai.action import Action
from ai.ball_types_bounty_hunter import BountyHunter
from ai.game_modes import BountyHuntMode, BossFightMode

class MockWorld:
    def __init__(self):
        self.game_mode = BountyHuntMode()

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

class MockBall:
    def __init__(self, id, ball_type="warrior"):
        self.id = id
        self.ball_type = ball_type
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.is_bounty = False
        self.team = "Red"
        self.x = 0
        self.y = 0

def test_bounty_hunter_double_damage_bounty():
    world = MockWorld()
    hunter = MockBall(1, "bounty_hunter")
    hunter.damage = 25.0

    target = MockBall(2, "warrior")
    target.is_bounty = True

    action = Action(hunter, world)
    action._attempt_damage(hunter, target)

    # 100 - 25*2 = 50
    assert target.hp == 50.0

def test_bounty_hunter_normal_damage_non_bounty():
    world = MockWorld()
    hunter = MockBall(1, "bounty_hunter")
    hunter.damage = 25.0

    target = MockBall(2, "warrior")
    target.is_bounty = False

    action = Action(hunter, world)
    action._attempt_damage(hunter, target)

    # 100 - 25 = 75
    assert target.hp == 75.0

def test_bounty_hunter_double_damage_boss():
    world = MockWorld()
    world.game_mode = BossFightMode()
    hunter = MockBall(1, "bounty_hunter")
    hunter.damage = 25.0

    target = MockBall(2, "warrior")
    target.team = "Boss"

    action = Action(hunter, world)
    action._attempt_damage(hunter, target)

    # 100 - 25*2 = 50
    assert target.hp == 50.0
