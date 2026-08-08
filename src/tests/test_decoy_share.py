import pytest
from system.test_crowd_system import MockBall, MockWorld
from ai.action import Action

def test_decoy_shares_damage_and_buffs():
    # Setup owner and decoy
    owner = MockBall(1, "team1", "player")
    owner.x = 100
    owner.y = 100
    owner.hp = 100.0
    owner.max_hp = 100.0

    decoy = MockBall(2, "team1", "player")
    decoy.is_decoy = True
    decoy.owner_id = 1
    decoy.x = 150
    decoy.y = 150
    decoy.hp = 100.0
    decoy.max_hp = 100.0
    decoy.decoy_timer = 5.0

    world = MockWorld()
    world.balls = [owner, decoy]

    action = Action(decoy, world)

    # 1. Damage share
    decoy._mock_damage_taken = 20.0 # Will subtract 20.0 hp in execute()

    action.execute("dummy", 0.016)

    assert decoy.hp == 80.0
    assert owner.hp == 90.0 # Shared 10 damage

    # 2. Heal share
    decoy._mock_damage_taken = -10.0 # Heal 10.0 hp

    action.execute("dummy", 0.016)

    assert decoy.hp == 90.0
    assert owner.hp == 95.0 # Shared 5 heal

    # 3. Buff share
    decoy._mock_damage_taken = 0.0
    decoy.damage_boost_timer = 5.0

    action.execute("dummy", 0.016)

    assert getattr(owner, 'damage_boost_timer', 0.0) == 5.0
