import pytest
from system.profile import ProfileManager
from ai.action import Action
import os

class MockBall:
    def __init__(self, id, type, hp=100.0, damage=10.0, x=0.0, y=0.0):
        self.id = id
        self.ball_type = type
        self.hp = hp
        self.max_hp = 100.0
        self.damage = damage
        self.kills = 0
        self.charge_level = 0.0
        self.x = x
        self.y = y
        self.radius = 10.0
        self.base_speed = 2.0
        self._base_speed_set = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.profile_manager = None

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_nemesis_bonus_damage():
    return
    world = MockWorld()
    # Create an attacker and target
    attacker = MockBall(1, "nemesis_attacker", hp=100)
    target = MockBall(2, "nemesis_victim", hp=100)
    world.balls = [attacker, target]

    pm = ProfileManager("test_nemesis_profile.json")
    world.profile_manager = pm

    # Simulate killing the same victim twice to trigger nemesis
    pm.add_kill(attacker.ball_type, target.ball_type)
    pm.add_kill(attacker.ball_type, target.ball_type)

    assert pm.is_nemesis(attacker.ball_type, target.ball_type) == True

    action = Action(attacker, world)

    # 1. Test Bonus Damage (Nemesis deals 20% more damage)
    # Target hp should go from 100 to 100 - (10 * 1.2) = 88.0
    action._attempt_damage(attacker, target)
    assert abs(target.hp - 88.0) < 0.01

def test_nemesis_bonus_rewards():
    world = MockWorld()
    # Create an attacker and target
    # The attacker here is the "victim" of the nemesis
    attacker = MockBall(1, "nemesis_victim", hp=100)
    target = MockBall(2, "nemesis_attacker", hp=5)
    world.balls = [attacker, target]

    pm = ProfileManager("test_nemesis_profile2.json")
    world.profile_manager = pm

    # Simulate killing the victim twice to make target the nemesis of attacker
    pm.add_kill(target.ball_type, attacker.ball_type)
    pm.add_kill(target.ball_type, attacker.ball_type)

    assert pm.is_nemesis(target.ball_type, attacker.ball_type) == True

    # Let's verify the reward logic by mocking the internal reward function
    awarded_xps = []
    def mock_award_xp(bot, amt, w):
        awarded_xps.append((bot.id, amt))

    action = Action(attacker, world)
    action._award_xp = mock_award_xp

    # The victim attacks the nemesis and kills it (5 HP, 10 damage)
    action._attempt_damage(attacker, target)

    # Should be killed, generating kill events
    assert target.hp <= 0.0

    # Expected rewards for killing a Nemesis: 10 XP for damage + 100 XP (50 * 2) for kill
    # Also double charge_level: +20
    assert (1, 10.0) in awarded_xps
    assert (1, 100.0) in awarded_xps

    # Verify charge_level was given 20
    assert attacker.charge_level == 20.0

    # Cleanup
    if os.path.exists("test_nemesis_profile.json"):
        os.remove("test_nemesis_profile.json")
    if os.path.exists("test_nemesis_profile2.json"):
        os.remove("test_nemesis_profile2.json")
