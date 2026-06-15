import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_brain import BallBrain
from ai.decision import Decision
from ai.action import Action

class MockBall:
    def __init__(self, difficulty="medium", personality="idle"):
        self.difficulty = difficulty
        self.personality = personality
        self.hp = 100
        self.max_hp = 100
        self.current_action = "idle"
        self.skill_timer = 0.0
        self.skill_used = False
        self.x = 10
        self.y = 10
        self.speed = 10
        self.radius = 10
        self.perception_radius = 100
        self.ball_type = "mock"
        self.alive = True
        self.kills = 0

    def use_skill(self):
        self.skill_used = True

    def get_hp_percent(self):
        return float(self.hp) / float(self.max_hp)

class MockWorld:
    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": []
        }

def test_ball_brain_reaction_time_hard():
    ball = MockBall(difficulty="hard")
    world = MockWorld()
    brain = BallBrain(ball, world)

    # Process once
    brain.process(0.016)
    assert brain.reaction_timer == 0.0 # Hard always resets to 0.0

    # Next frame should also process logic
    brain.process(0.016)
    assert brain.reaction_timer == 0.0

def test_ball_brain_reaction_time_easy():
    ball = MockBall(difficulty="easy")
    world = MockWorld()
    brain = BallBrain(ball, world)

    # Process once, timer should be set to 0.5
    brain.process(0.016)
    assert brain.reaction_timer == 0.5

    # Process again with small delta, timer should decrease but not reset
    brain.process(0.1)
    assert brain.reaction_timer == 0.4

    # Process with large delta, timer should reset
    brain.process(0.5)
    assert brain.reaction_timer == 0.5

def test_decision_chaos():
    # Since chaos is random, we just verify it runs without error and returns a string
    ball = MockBall(difficulty="chaos")
    world = MockWorld()
    decision = Decision(ball, world)

    perception = {
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "threat_level": 0.0,
        "opportunity_score": 0.0,
        "enemies": [],
        "boosters": [],
        "allies": []
    }

    actions = set()
    for _ in range(50):
        action = decision.choose_action(perception, "neutral")
        actions.add(action)

    # It should eventually pick more than just 'idle' due to chaos randomness
    assert len(actions) > 1

def test_action_skill_easy_fizzle():
    ball = MockBall(difficulty="easy")
    world = MockWorld()
    action_layer = Action(ball, world)

    successes = 0
    failures = 0

    for _ in range(100):
        ball.skill_used = False
        action_layer._use_skill()
        if ball.skill_used:
            successes += 1
        else:
            failures += 1

    # With 30% failure rate, we should see some failures over 100 tries
    assert failures > 0
    assert successes > 0
