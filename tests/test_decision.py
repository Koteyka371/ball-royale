import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.decision import Decision

class MockBall:
    def __init__(self, hp=100, max_hp=100, personality="idle"):
        self.hp = hp
        self.max_hp = max_hp
        self.personality = personality

    def get_hp_percent(self):
        if self.max_hp == 0:
            return 0.0
        return float(self.hp) / float(self.max_hp)

class MockWorld:
    pass

def test_decision_fear_flee():
    ball = MockBall(hp=20, max_hp=100)
    world = MockWorld()
    decision = Decision(ball, world)

    # Even if there are enemies and boosters, fear should prioritize flee
    perception = {
        "danger_level": 0.5,
        "opportunity_level": 0.8,
        "enemies": [1, 2],
        "boosters": [1, 2, 3]
    }
    action = decision.choose_action(perception, "fear")
    assert action == "flee"

def test_decision_defend_high_danger():
    ball = MockBall(hp=100, max_hp=100, personality="idle")
    world = MockWorld()
    decision = Decision(ball, world)

    # High danger level (>0.7) should prioritize defend over attack
    perception = {
        "danger_level": 0.8,
        "opportunity_level": 0.1,
        "enemies": [1, 2, 3, 4],
        "boosters": []
    }
    action = decision.choose_action(perception, "neutral")
    assert action == "defend"

def test_decision_greed_opportunistic():
    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    decision = Decision(ball, world)

    # Greed with boosters should prioritize opportunistic
    perception = {
        "danger_level": 0.1,
        "opportunity_level": 0.9,
        "enemies": [1],
        "boosters": [1, 2]
    }
    action = decision.choose_action(perception, "greed")
    assert action == "opportunistic"

def test_decision_rage_attack():
    ball = MockBall(hp=100, max_hp=100, personality="idle")
    world = MockWorld()
    decision = Decision(ball, world)

    # Rage should prioritize attack
    perception = {
        "danger_level": 0.3,
        "opportunity_level": 0.0,
        "enemies": [1],
        "boosters": []
    }
    action = decision.choose_action(perception, "rage")
    assert action == "attack"

def test_decision_fallback_personality():
    ball = MockBall(hp=100, max_hp=100, personality="scout")
    world = MockWorld()
    decision = Decision(ball, world)

    # Empty perception, neutral emotion -> should fall back to personality
    perception = {
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "enemies": [],
        "boosters": []
    }
    action = decision.choose_action(perception, "neutral")
    assert action == "scout"
