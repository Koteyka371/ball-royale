import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.decision import Decision

class MockBall:
    def __init__(self, hp=100, max_hp=100, personality="idle", skill_timer=0.0):
        self.hp = hp
        self.max_hp = max_hp
        self.personality = personality
        self.skill_timer = skill_timer

    def get_hp_percent(self):
        if self.max_hp == 0:
            return 0.0
        return float(self.hp) / float(self.max_hp)

class MockWorld:
    pass

def test_decision_fear_flee():
    ball = MockBall(hp=20, max_hp=100)
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.5, "opportunity_level": 0.8,
        "threat_level": 2.0, "opportunity_score": 0.6,
        "enemies": [1, 2], "boosters": [1, 2, 3], "allies": []
    }
    action = decision.choose_action(perception, "fear")
    assert action == "flee"

def test_decision_defend_high_danger():
    ball = MockBall(hp=100, max_hp=100, personality="idle")
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.8, "opportunity_level": 0.1,
        "threat_level": 3.0, "opportunity_score": 0.1,
        "enemies": [1, 2, 3, 4], "boosters": [], "allies": []
    }
    action = decision.choose_action(perception, "neutral")
    assert action == "defend"

def test_decision_greed_collect_booster():
    ball = MockBall(hp=100, max_hp=100)
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.1, "opportunity_level": 0.9,
        "threat_level": 0.5, "opportunity_score": 0.8,
        "enemies": [1], "boosters": [1, 2], "allies": []
    }
    action = decision.choose_action(perception, "greed")
    assert action == "collect_booster"

def test_decision_rage_attack():
    ball = MockBall(hp=100, max_hp=100, personality="idle")
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.3, "opportunity_level": 0.0,
        "threat_level": 1.0, "opportunity_score": 0.0,
        "enemies": [1], "boosters": [], "allies": []
    }
    action = decision.choose_action(perception, "rage")
    assert action == "attack"

def test_decision_fallback_personality():
    ball = MockBall(hp=100, max_hp=100, personality="scout")
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.0, "opportunity_level": 0.0,
        "threat_level": 0.0, "opportunity_score": 0.0,
        "enemies": [], "boosters": [], "allies": []
    }
    action = decision.choose_action(perception, "neutral")
    assert action == "collect_booster"

def test_decision_use_skill():
    ball = MockBall(hp=80, max_hp=100, skill_timer=0.0)
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.4, "opportunity_level": 0.0,
        "threat_level": 2.0, "opportunity_score": 0.0,
        "enemies": [1, 2], "boosters": [], "allies": []
    }
    action = decision.choose_action(perception, "neutral")
    assert action == "use_skill"

def test_decision_chase_assassin():
    ball = MockBall(hp=100, max_hp=100, personality="assassin")
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.3, "opportunity_level": 0.0,
        "threat_level": 1.0, "opportunity_score": 0.0,
        "enemies": [1], "boosters": [], "allies": []
    }
    action = decision.choose_action(perception, "neutral")
    assert action == "chase"

def test_decision_no_enemies_personality_fallback():
    ball = MockBall(hp=100, max_hp=100, personality="warrior")
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.0, "opportunity_level": 0.0,
        "threat_level": 0.0, "opportunity_score": 0.0,
        "enemies": [], "boosters": [], "allies": []
    }
    action = decision.choose_action(perception, "neutral")
    assert action == "attack"

def test_decision_heroism_emotion():
    ball = MockBall(hp=100, max_hp=100, personality="idle")
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.1, "opportunity_level": 0.0,
        "threat_level": 0.1, "opportunity_score": 0.0,
        "enemies": [1], "boosters": [], "allies": [2]
    }
    action = decision.choose_action(perception, "heroism")
    # Defend should be favored strongly, or attack depending on exact scores.
    # Heroism adds +80 to defend, +50 to attack. With 1 ally, defend gets another +0 (since hp_percent=1.0).
    # Since danger is low, defend = 80 + 2 = 82. Attack = 10 + 50 = 60.
    assert action == "defend"

def test_decision_ally_advantage():
    ball = MockBall(hp=100, max_hp=100, personality="idle")
    decision = Decision(ball, MockWorld())
    perception = {
        "danger_level": 0.1, "opportunity_level": 0.0,
        "threat_level": 0.1, "opportunity_score": 0.0,
        "enemies": [1], "boosters": [], "allies": [2, 3, 4]
    }
    action = decision.choose_action(perception, "neutral")
    # 3 allies vs 1 enemy. Attack gets +10 (1 enemy) + (3 - 1) * 15 = 40.
    # Idle is 1. Defend is 2.
    assert action == "attack"
