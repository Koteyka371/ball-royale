import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ai.ball_types_soul_linker import SoulLinker

class MockTarget:
    def __init__(self, hp=150.0, speed=200.0, ball_type="normal"):
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.base_speed = speed
        self.alive = True
        self.ball_type = ball_type
        self.x = 10.0
        self.y = 10.0
        self.radius = 10.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_soul_linker_initialization():
    linker = SoulLinker(1, 0, 0)
    assert linker.BALL_TYPE == "soul_linker"
    assert not linker.has_linked
    assert linker.linked_enemy is None

def test_soul_linker_pairing():
    linker = SoulLinker(1, 0, 0)
    target = MockTarget(hp=200.0, speed=150.0)

    # Not linked yet, calling attack with target should link
    linker.attack(0.1, target)

    assert linker.has_linked
    assert linker.linked_enemy == target
    assert linker.hp == 200.0
    assert linker.max_hp == 200.0
    assert linker.speed == 150.0
    assert linker.base_speed == 150.0

def test_soul_linker_damage_distribution():
    linker = SoulLinker(1, 0, 0)
    target = MockTarget(hp=100.0, speed=100.0)

    linker.attack(0.1, target)
    assert linker.has_linked

    # Linker takes 40 damage
    linker.take_damage(40.0)

    # 50% distributed to target (20), 50% applied to linker (20)
    assert linker.hp == 80.0
    assert target.hp == 80.0

def test_soul_linker_damage_distribution_target_dead():
    linker = SoulLinker(1, 0, 0)
    target = MockTarget(hp=100.0, speed=100.0)

    linker.attack(0.1, target)

    target.alive = False

    # Linker takes 40 damage, but target is dead
    linker.take_damage(40.0)

    # 100% applied to linker since target is dead
    assert linker.hp == 60.0

def test_soul_linker_damage_kills_target():
    linker = SoulLinker(1, 0, 0)
    target = MockTarget(hp=10.0, speed=100.0)

    linker.attack(0.1, target)

    # Linker takes 30 damage
    # 15 distributed to target -> target dies
    linker.take_damage(30.0)

    assert linker.hp == -5.0 # Linker also dies (10 - 15)
    assert target.hp == -5.0
    assert not target.alive
    assert not linker.alive
