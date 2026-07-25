import pytest
import os
from system.profile import ProfileManager
from ai.action import Action
from ai.game_modes import NemesisSustainMode

class MockBall:
    def __init__(self, id, ball_type, hp=100.0, max_hp=100.0, damage=10.0):
        self.id = id
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = max_hp
        self.damage = damage
        self.x = 0
        self.y = 0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.profile_manager = None
        self.current_mode_name = ""

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_nemesis_sustain_healing():
    world = MockWorld()
    world.current_mode_name = "Nemesis Sustain"

    attacker = MockBall(1, "hunter", hp=50.0, max_hp=100.0, damage=20.0)
    target = MockBall(2, "prey", hp=100.0, max_hp=100.0)
    world.balls = [attacker, target]

    pm = ProfileManager("test_sustain_profile.json")
    world.profile_manager = pm

    # Simulate killing to make hunter nemesis of prey (Wait, if hunter kills prey, prey is victim, hunter is killer)
    # The action logic checks: pm.is_nemesis(target.ball_type, attacker.ball_type)
    # This means attacker is the nemesis of the target.
    # is_nemesis(victim, killer) -> true if killer is nemesis of victim.
    # So we need to add_kill(killer_type, victim_type).
    pm.add_kill(target.ball_type, attacker.ball_type)
    pm.add_kill(target.ball_type, attacker.ball_type)

    assert pm.is_nemesis(target.ball_type, attacker.ball_type) == True

    action = Action(attacker, world)

    # Hunter attacks Prey. Base damage is 20, target loses 20 HP, attacker heals 20 HP.
    action._attempt_damage(attacker, target)

    # Assert damage dealt
    assert abs(target.hp - 80.0) < 0.1

    # Assert healing
    assert abs(attacker.hp - 70.0) < 0.1

    if os.path.exists("test_sustain_profile.json"):
        os.remove("test_sustain_profile.json")

def test_nemesis_sustain_no_healing_normal_mode():
    world = MockWorld()
    world.current_mode_name = "Normal Mode"

    attacker = MockBall(1, "hunter", hp=50.0, max_hp=100.0, damage=20.0)
    target = MockBall(2, "prey", hp=100.0, max_hp=100.0)
    world.balls = [attacker, target]

    pm = ProfileManager("test_sustain_profile2.json")
    world.profile_manager = pm

    pm.add_kill(target.ball_type, attacker.ball_type)
    pm.add_kill(target.ball_type, attacker.ball_type)

    action = Action(attacker, world)

    action._attempt_damage(attacker, target)

    # Attacker shouldn't heal
    assert abs(attacker.hp - 50.0) < 0.1

    if os.path.exists("test_sustain_profile2.json"):
        os.remove("test_sustain_profile2.json")
