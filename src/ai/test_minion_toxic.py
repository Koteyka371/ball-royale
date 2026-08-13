from ai.action import Action
from ai.test_action_advanced import MockBall, MockWorld
import sys

class MockArena:
    def __init__(self):
        self.hazards = []

def test_minion_toxic_sludge_decay():
    world = MockWorld()
    world.arena = MockArena()
    world.mutators = ["toxic_sludge"]
    world.mutators_active = True

    # Patch _deal_damage to actually deal damage for testing purposes
    def mock_deal_damage(attacker, target, dmg=None):
        if dmg is not None:
            target.hp -= dmg
        else:
            target.hp -= getattr(attacker, "damage", 10.0)
    world._deal_damage = mock_deal_damage

    minion = MockBall()
    minion.ball_type = "minion"
    minion.is_minion = True
    minion.is_enraged = True
    minion.enrage_timer = 5.0
    minion.hp = 10.0
    minion.max_hp = 100.0
    minion.team = "undead"
    minion.x = 0
    minion.y = 0
    minion.id = 1

    enemy = MockBall()
    enemy.hp = 100.0
    enemy.team = "heroes"
    enemy.x = 10
    enemy.y = 0
    enemy.alive = True
    enemy.id = 2

    world.balls = [minion, enemy]

    action = Action(minion, world)
    # Applying a delta large enough to trigger death from decay (20.0 * 1.0 = 20.0 > 10.0)
    action.execute(strategy="idle", delta=1.0)

    assert not getattr(minion, "alive", True)
    assert not getattr(minion, "is_enraged", True)

    # Since toxic_sludge is active, no explosion damage should be dealt to the enemy
    assert enemy.hp == 100.0

    # A poison_cloud hazard should have been spawned
    assert len(world.arena.hazards) == 1
    cloud = world.arena.hazards[0]
    assert getattr(cloud, "kind", "") == "poison_cloud"
    assert getattr(cloud, "radius", 0.0) == 120.0
    assert getattr(cloud, "damage", 0.0) == 10.0
    assert getattr(cloud, "duration", 0.0) == 5.0
