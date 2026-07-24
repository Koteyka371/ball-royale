import pytest
from system.profile import ProfileManager
from ai.action import Action
from ai.game_modes import NemesisVampirismMode
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
        self.game_mode = None
        self.events = []

    def add_event(self, t, d):
        self.events.append({'type': t, 'data': d})

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_nemesis_vampirism_healing():
    world = MockWorld()
    # Create an attacker and target
    attacker = MockBall(1, "hunter", hp=50) # Missing 50 HP
    target = MockBall(2, "nemesis", hp=100)
    world.balls = [attacker, target]

    pm = ProfileManager("test_nemesis_vamp_profile.json")
    world.profile_manager = pm
    world.game_mode = NemesisVampirismMode()

    # Make target the nemesis of attacker
    pm.add_kill(target.ball_type, attacker.ball_type)
    pm.add_kill(target.ball_type, attacker.ball_type)

    assert pm.is_nemesis(target.ball_type, attacker.ball_type) == True

    action = Action(attacker, world)

    # Dealing damage to your nemesis heals you
    # Action._attempt_damage handles damage processing
    action._attempt_damage(attacker, target)

    # Target takes 10 damage + 20% bonus against nemesis victim = actually the attacker is the victim here, so no bonus damage for attacker
    # Wait, if target is nemesis of attacker, target gets bonus damage. Attacker gets bonus rewards but NO bonus damage.
    # Attacker damage is 10. Target hp should be 90.
    # Attacker should heal for 10. So HP goes 50 -> 60
    assert target.hp == 90.0
    assert attacker.hp == 60.0

    # Ensure max hp cap is respected
    attacker.hp = 95.0
    action._attempt_damage(attacker, target)
    assert target.hp == 80.0
    assert attacker.hp == 100.0

    if os.path.exists("test_nemesis_vamp_profile.json"):
        os.remove("test_nemesis_vamp_profile.json")
