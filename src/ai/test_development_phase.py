import os
import pytest # type: ignore
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ai.development_phase import DevelopmentPhase

class MockBall:
    def __init__(self, speed, damage, max_hp, hp, color, skill, ball_type, alive, kills):
        self.speed = speed
        self.damage = damage
        self.max_hp = max_hp
        self.hp = hp
        self.color = color
        self.skill = skill
        self.ball_type = ball_type
        self.alive = alive
        self.kills = kills

def test_calculate_xp():
    dev_phase = DevelopmentPhase()

    # Alive, 0 kills -> 50 XP
    ball1 = MockBall(2.0, 15.0, 100.0, 100.0, "red", "dash", "warrior", True, 0)
    assert dev_phase.calculate_xp(ball1) == 50

    # Dead, 2 kills -> 40 XP
    ball2 = MockBall(2.0, 15.0, 100.0, 0.0, "red", "dash", "warrior", False, 2)
    assert dev_phase.calculate_xp(ball2) == 40

    # Alive, 3 kills -> 50 + 60 = 110 XP
    ball3 = MockBall(2.0, 15.0, 100.0, 100.0, "red", "dash", "warrior", True, 3)
    assert dev_phase.calculate_xp(ball3) == 110

def test_process_battle_results_no_upgrade():
    dev_phase = DevelopmentPhase(xp_for_upgrade=100)
    ball1 = MockBall(2.0, 15.0, 100.0, 100.0, "red", "dash", "warrior", True, 1) # 70 XP

    dev_phase.process_battle_results([ball1])

    # Check stats are unmodified
    assert ball1.max_hp == 100.0
    assert ball1.damage == 15.0
    assert ball1.speed == 2.0
    assert ball1.ball_type == "warrior"

    dna_hash = dev_phase._generate_dna_hash(dev_phase._extract_dna(ball1))
    assert dev_phase.xp_bank[dna_hash]["xp"] == 70
    assert dev_phase.xp_bank[dna_hash]["level"] == 1

def test_process_battle_results_with_upgrade():
    dev_phase = DevelopmentPhase(xp_for_upgrade=100)
    ball1 = MockBall(2.0, 15.0, 100.0, 50.0, "red", "dash", "warrior", True, 3) # 110 XP

    dev_phase.process_battle_results([ball1])

    # Check stats are upgraded
    assert ball1.max_hp >= 110.0
    assert ball1.damage >= 16.5
    assert ball1.speed >= 2.1
    assert ball1.hp >= 60.0
    assert ball1.ball_type == "warrior_developed"

    # The hash should be based on the ORIGINAL dna before it was upgraded
    base_dna = {
        "speed": 2.0,
        "damage": 15.0,
        "max_hp": 100.0,
        "color": "red",
        "skill": "dash",
        "ball_type": "warrior"
    }
    dna_hash = dev_phase._generate_dna_hash(base_dna)

    assert dev_phase.xp_bank[dna_hash]["xp"] == 10 # 110 - 100
    assert dev_phase.xp_bank[dna_hash]["level"] == 2

def test_spectator_ignored():
    dev_phase = DevelopmentPhase(xp_for_upgrade=100)
    spectator = MockBall(2.0, 15.0, 100.0, 100.0, "red", "dash", "spectator", True, 5) # Would be 150 XP

    dev_phase.process_battle_results([spectator])

    # Bank should be empty, no stats changed
    assert len(dev_phase.xp_bank) == 0
    assert spectator.ball_type == "spectator"

def test_multiple_battles_accumulate_xp():
    dev_phase = DevelopmentPhase(xp_for_upgrade=100)

    # Battle 1
    ball1 = MockBall(2.0, 15.0, 100.0, 100.0, "red", "dash", "warrior", True, 1) # 70 XP
    dev_phase.process_battle_results([ball1])

    # Battle 2 - Same exact DNA should match hash
    ball2 = MockBall(2.0, 15.0, 100.0, 100.0, "red", "dash", "warrior", True, 0) # 50 XP
    dev_phase.process_battle_results([ball2])

    # Should have upgraded (70 + 50 = 120 -> 20 remaining)
    assert ball2.ball_type == "warrior_developed"
    assert ball2.max_hp >= 110.0

    base_dna = {
        "speed": 2.0,
        "damage": 15.0,
        "max_hp": 100.0,
        "color": "red",
        "skill": "dash",
        "ball_type": "warrior"
    }
    dna_hash = dev_phase._generate_dna_hash(base_dna)
    assert dev_phase.xp_bank[dna_hash]["xp"] == 20
    assert dev_phase.xp_bank[dna_hash]["level"] == 2

def test_skill_tree_applied():
    dev_phase = DevelopmentPhase(xp_for_upgrade=100)

    # We want level 2 upgrade, meaning the ball levels up. 110 XP -> leveled up
    # However we need level 2 to get a skill upgrade.
    # Initially it's level 1, +1 level -> level 2.
    ball1 = MockBall(2.0, 15.0, 100.0, 50.0, "red", "dash", "warrior", True, 3) # 110 XP
    dev_phase.process_battle_results([ball1])

    # Should have a passive now from level 2
    assert hasattr(ball1, 'passives')
    assert len(ball1.passives) == 1
    assert ball1.passives[0] in ["Thick Skin", "Sprinter", "Sharp Edges"]
