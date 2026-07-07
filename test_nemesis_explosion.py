import pytest
import os
import math
from src.ai.action import Action
from src.system.profile import ProfileManager

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
        self.skill_timer = 0
        self.skill = "nemesis_explosion"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.profile_manager = None
        self.arena = type("Arena", (), {"hazards": [], "rooms": []})()

    def _deal_damage(self, attacker, target):
        pass

def test_nemesis_explosion_skill():
    world = MockWorld()

    attacker = MockBall(1, "attacker_type", hp=100, x=0, y=0)
    attacker.skill = "nemesis_explosion"

    nemesis1 = MockBall(2, "nemesis_type_1", hp=100, x=50, y=0)
    nemesis2 = MockBall(3, "nemesis_type_2", hp=100, x=0, y=50)
    normal_enemy = MockBall(4, "normal_type", hp=100, x=-50, y=0)
    far_enemy = MockBall(5, "nemesis_type_1", hp=100, x=200, y=200) # Out of range

    world.balls = [attacker, nemesis1, nemesis2, normal_enemy, far_enemy]

    pm = ProfileManager("test_nemesis_explosion_profile.json")
    world.profile_manager = pm

    # Make them nemeses
    pm.add_kill(nemesis1.ball_type, attacker.ball_type)
    pm.add_kill(nemesis1.ball_type, attacker.ball_type)

    pm.add_kill(nemesis2.ball_type, attacker.ball_type)
    pm.add_kill(nemesis2.ball_type, attacker.ball_type)

    # Normal enemy is not a nemesis

    # Out of range enemy is a nemesis
    pm.add_kill(far_enemy.ball_type, attacker.ball_type)
    pm.add_kill(far_enemy.ball_type, attacker.ball_type)

    assert pm.is_nemesis(nemesis1.ball_type, attacker.ball_type) == True
    assert pm.is_nemesis(nemesis2.ball_type, attacker.ball_type) == True
    assert pm.is_nemesis(normal_enemy.ball_type, attacker.ball_type) == False

    # Give everyone a fake take_damage
    def make_take_damage(b):
        def take_damage(dmg):
            b.hp -= dmg
        return take_damage

    for b in world.balls:
        b.take_damage = make_take_damage(b)

    action = Action(attacker, world)

    # Set enemies so action._get_enemies returns our mocked balls
    def mock_get_enemies():
        return [b for b in world.balls if b != attacker]
    action._get_enemies = mock_get_enemies

    # Trigger the skill
    action._use_skill()

    # 2 nemeses on field (nemesis1, nemesis2, far_enemy) -> 3 nemeses alive
    # Base damage 50 + (3 * 25) = 125 damage
    # Radius 100 + (3 * 20) = 160 radius

    assert nemesis1.hp == -25.0
    assert nemesis2.hp == -25.0
    assert normal_enemy.hp == -25.0
    assert far_enemy.hp == 100.0 # Out of range (282 > 160)

    if os.path.exists("test_nemesis_explosion_profile.json"):
        os.remove("test_nemesis_explosion_profile.json")
