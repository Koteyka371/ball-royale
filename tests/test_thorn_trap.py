import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action

class MockWorld:
    def __init__(self):
        self._deal_damage_calls = []

    def _deal_damage(self, target, attacker):
        self._deal_damage_calls.append((target.id, attacker.id, target.damage))
        # Usually _deal_damage does target.hp -= attacker.damage
        # Since target and attacker are swapped in reflection logic:
        # attacker takes damage equal to target.damage
        attacker.hp -= getattr(target, 'damage', 10.0)

class MockBall:
    def __init__(self, id, team, hp=100.0, damage=10.0):
        self.id = id
        self.team = team
        self.hp = hp
        self.damage = damage
        self.thorn_aura_timer = 0.0

def test_thorn_friendly_fire():
    world = MockWorld()

    attacker = MockBall(1, "TeamA", hp=100, damage=25)
    target = MockBall(2, "TeamA", hp=100, damage=10) # Same team

    target.thorn_aura_timer = 5.0

    action = Action(attacker.id, world)
    action.ball = attacker

    action._attempt_damage(attacker, target)

    # Since target has thorn and it's friendly fire, attacker should take the damage
    assert attacker.hp == 75 # 100 - 25
    assert target.hp == 100

    assert len(world._deal_damage_calls) == 1
    # Check that _deal_damage was called with (target, attacker)
    # wait, my mock records (target.id, attacker.id, target.damage)
    called_t, called_a, dmg = world._deal_damage_calls[0]
    assert called_t == 2
    assert called_a == 1
    assert dmg == 25 # Original damage of attacker

def test_thorn_enemy_fire():
    world = MockWorld()

    attacker = MockBall(1, "TeamA", hp=100, damage=25)
    target = MockBall(2, "TeamB", hp=100, damage=10) # Different team

    target.thorn_aura_timer = 5.0

    action = Action(attacker.id, world)
    action.ball = attacker

    # Redefine world._deal_damage for normal flow
    world._deal_damage_calls = []
    def normal_deal_damage(att, tgt):
        tgt.hp -= att.damage
        world._deal_damage_calls.append((att.id, tgt.id, att.damage))
    world._deal_damage = normal_deal_damage

    action._attempt_damage(attacker, target)

    # Since it's an enemy, thorn should not reflect friendly fire
    assert attacker.hp == 100
    assert target.hp == 75 # 100 - 25
