import pytest
import math
from ai.action import Action
from ai.ball_types_mirage_master import MirageMaster

class MockWorld:
    def __init__(self):
        self.balls = []
        self.tick = 0
        self.next_id = 100

    def _deal_damage(self, target, attacker, dmg=None):
        if dmg is None:
            dmg = attacker.damage if hasattr(attacker, "damage") else 10.0
        if hasattr(target, "take_damage"):
            target.take_damage(dmg)
        elif hasattr(target, "hp"):
            target.hp -= dmg

def test_mirage_swarm_skill():
    world = MockWorld()
    ball = MirageMaster(1, 100, 100)
    world.balls.append(ball)
    action = Action(ball, world)

    ball.skill_timer = 0
    action.execute("use_skill", 1.0)

    decoys = [b for b in world.balls if b != ball]

    assert len(decoys) == 3, f"Expected 3 decoys, got {len(decoys)}"
    for decoy in decoys:
        assert getattr(decoy, "is_illusion", False) == True
        assert getattr(decoy, "is_active_clone", False) == True
        assert getattr(decoy, "mimic_owner", None) == 1
        assert getattr(decoy, "is_decoy", False) == True
        assert getattr(decoy, "decoy_type", "") == "explosive"
        assert decoy.hp == 1.0
        assert decoy.max_hp == 1.0

def test_mirage_swarm_recast():
    world = MockWorld()
    ball = MirageMaster(1, 100, 100)
    world.balls.append(ball)
    action = Action(ball, world)

    ball.skill_timer = 0
    action.execute("use_skill", 1.0)

    assert len(world.balls) == 4

    ball.skill_timer = 0
    action.execute("use_skill", 1.0)

    decoys = [b for b in world.balls if getattr(b, "is_illusion", False) and getattr(b, "alive", True)]
    assert len(decoys) == 0, "Decoys should be cleared on recast"

    ball.skill_timer = 0
    action.execute("use_skill", 1.0)

    decoys = [b for b in world.balls if getattr(b, "is_illusion", False) and getattr(b, "alive", True)]
    assert len(decoys) == 3, "New decoys should be spawned"
