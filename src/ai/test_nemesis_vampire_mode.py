import pytest
from ai.game_modes import NemesisVampireMode
from ai.action import Action
from unittest.mock import Mock

class MockEntity:
    def __init__(self):
        pass

class MockWorld:
    def __init__(self):
        self.events = []

class MockProfileManager:
    def is_nemesis(self, t1, t2):
        if t1 == "nemesis_hunter" and t2 == "victim": return True
        return False

def test_nemesis_vampire_mode_tick():
    mode = NemesisVampireMode()
    b1 = MockEntity()
    b1.id = 1
    b1.hp = 100.0
    b1.alive = True
    b1.ball_type = "nemesis_hunter"
    b1.base_speed = 1.0
    b1.speed_multiplier = 1.0
    b1.damage = 10.0
    b1.damage_multiplier = 1.0
    b1.base_damage = 10.0
    b1.has_attacked = False
    b1.base_damage = 10.0
    b1.damage_multiplier = 1.0
    b1.size_multiplier = 1.0

    b2 = MockEntity()
    b2.id = 2
    b2.hp = 100.0
    b2.alive = True
    b2.ball_type = "victim"
    b2.base_speed = 1.0
    b2.speed_multiplier = 1.0
    b2.damage = 10.0
    b2.base_damage = 10.0
    b2.damage_multiplier = 1.0
    b2.size_multiplier = 1.0

    world = MockWorld()
    world.profile_manager = MockProfileManager()
    world.current_mode_name = "Nemesis Vampire"
    world.leaderboard_manager = Mock()

    # Simulate time passing to trigger HP drain
    for _ in range(63): # ~1 second at 0.016 delta
        mode.tick(world, [b1, b2], delta=0.016)

    assert b1.hp < 100.0
    assert b2.hp < 100.0

def test_nemesis_vampire_heal():
    b1 = MockEntity()
    b1.id = 1
    b1.hp = 50.0
    b1.max_hp = 100.0
    b1.damage = 10.0
    b1.damage_multiplier = 1.0
    b1.base_damage = 10.0
    b1.has_attacked = False
    b1.team = "Red"
    b1.ball_type = "nemesis_hunter"
    b1.alive = True
    b1.stutter_timer = 0.0
    b1.lifesteal = 0.0
    b1.vampiric = False
    b1.charge_level = 0.0

    b2 = MockEntity()
    b2.id = 2
    b2.hp = 100.0
    b2.team = "Blue"
    b2.ball_type = "victim"
    b2.alive = True
    b2.intangible = False

    world = MockWorld()
    world.profile_manager = MockProfileManager()
    world.current_mode_name = "Nemesis Vampire"
    world._deal_damage = Mock()
    b1.attack_timer = -1.0

    # We simulate b1 attacking b2 via Action._attack
    action = Action(b1, world)
    b1.attack_timer = -1.0
    # Give them range
    b1.x, b1.y = 100, 100
    b2.x, b2.y = 100, 105
    b1.range = 20.0
    b1.speed = 1.0

    # Call internal attack logic where the heal resides
    action.target = b2
    action._get_enemies = lambda: [b2]
    action._get_target = lambda enemies: enemies[0]
    action._attack(0.016)

    # Since b1 damaged b2, and b1 is nemesis of b2, b1 should heal
    # Formula: hp = min(hp + dmg * 2.5, max_hp)
    # hp = min(50 + 10 * 2.5, 100) = 75
    assert b1.hp == 75.0
