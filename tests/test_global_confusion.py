import pytest
from ai.action import Action
from ai.ball_types_chaos_lord import ChaosLord
from ai.ball_types_easy import Easy

class MockWorld:
    def __init__(self):
        self.balls = []
        self.tick = 0
        self.next_id = 1000

    def _deal_damage(self, attacker, target):
        target.take_damage(attacker.damage)

def test_global_confusion_skill():
    world = MockWorld()

    # Create the chaos lord
    chaos_lord = ChaosLord(1, x=0, y=0)
    chaos_lord.skill = "global_confusion"
    world.balls.append(chaos_lord)

    # Create some other balls
    ball1 = Easy(2, x=10, y=10)
    ball2 = Easy(3, x=20, y=20)
    world.balls.append(ball1)
    world.balls.append(ball2)

    action = Action(chaos_lord, world)

    assert len(world.balls) == 3

    # Use the skill
    action._use_skill()

    # There should now be 6 balls (3 original + 3 clones)
    assert len(world.balls) == 6

    clones = world.balls[3:]
    assert len(clones) == 3

    for clone in clones:
        assert getattr(clone, "is_illusion", False) is True
        assert getattr(clone, "is_active_clone", False) is True
        assert getattr(clone, "illusion_timer", 0.0) == 15.0
        assert getattr(clone, "skill", "dummy") is None
        assert getattr(clone, "SKILL", "dummy") is None

    # Let's call it again, it shouldn't clone the clones
    chaos_lord.skill_timer = 0
    action._use_skill()

    # 3 original * 2 clones = 6 new clones + 3 originals + 3 existing clones = 12 total
    # But actually, wait:
    # 2nd call: original balls are 3, so it adds 3 more clones. The existing clones are ignored.
    # Total balls: 6 + 3 = 9.
    assert len(world.balls) == 9
