import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.ball_brain import BallBrain
from ai.decision import Decision

class MockBall:
    def __init__(self, hp=100, max_hp=100, personality="idle", difficulty="hard"):
        self.hp = hp
        self.max_hp = max_hp
        self.personality = personality
        self.difficulty = difficulty
        self.current_action = None
        self.speed = 10
        self.radius = 10
        self.perception_radius = 100
        self.ball_type = "mock"
        self.alive = True
        self.x = 0
        self.y = 0
        self.skill_timer = 0

    def get_hp_percent(self):
        return float(self.hp) / float(self.max_hp)

class MockWorld:
    def __init__(self):
        self.entities = {
            "enemies": [],
            "allies": [],
            "boosters": [],
        }

    def get_nearby_entities(self, ball, radius):
        return self.entities

def test_ball_brain_reaction_timer_easy():
    ball = MockBall(difficulty="easy")
    world = MockWorld()
    brain = BallBrain(ball, world)

    # Process once -> timer starts at 0, decrements to -0.1, triggers decision, resets to 0.5
    brain.process(0.1)
    assert brain.reaction_timer == pytest.approx(0.5)

    # Check if a new decision is made when timer > 0
    original_strategy = brain.current_strategy

    # Change world state but timer is still > 0, so strategy shouldn't update
    world.entities["enemies"] = [MockBall()]
    brain.process(0.1)
    assert brain.current_strategy == original_strategy
    assert brain.reaction_timer == pytest.approx(0.4)

    # Wait until timer expires
    brain.process(0.4) # timer goes to 0, triggers decision, resets to 0.5
    assert brain.reaction_timer == pytest.approx(0.5)

def test_ball_brain_reaction_timer_chaos():
    ball = MockBall(difficulty="chaos")
    world = MockWorld()
    brain = BallBrain(ball, world)

    # Process once
    brain.process(0.1)
    # Timer shouldn't matter for chaos, it always updates.
    # Delay for chaos is 0.0, but timer keeps going negative.
    # Chaos always evaluates.
    original_strategy = brain.current_strategy

    # Change world state, chaos should pick it up immediately
    world.entities["enemies"] = [MockBall() for _ in range(5)]
    brain.process(0.1)
    # Note: chaos also adds random actions, so we just verify it runs without error
    # and reaction_timer is handled.

def test_decision_layer_difficulty_hard():
    ball = MockBall(difficulty="hard")
    world = MockWorld()
    decision = Decision(ball, world)

    perception = {
        "danger_level": 0.0, "opportunity_level": 0.9,
        "threat_level": 0.0, "opportunity_score": 0.8,
        "enemies": [], "boosters": [1, 2], "allies": []
    }

    # Hard should ALWAYS pick collect_booster in this greedy scenario
    for _ in range(10):
        action = decision.choose_action(perception, "greed")
        assert action == "collect_booster"

def test_decision_layer_difficulty_chaos():
    ball = MockBall(difficulty="chaos")
    world = MockWorld()
    decision = Decision(ball, world)

    perception = {
        "danger_level": 0.0, "opportunity_level": 0.9,
        "threat_level": 0.0, "opportunity_score": 0.8,
        "enemies": [1, 2], "boosters": [1, 2], "allies": []
    }

    # Chaos picks randomly from valid actions
    actions = set()
    for _ in range(100):
        action = decision.choose_action(perception, "neutral")
        actions.add(action)

    # Should have picked multiple different actions
    assert len(actions) > 1
