import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.neural_network_brain import NeuralNetworkBrain
from ai.neural_decision import NeuralDecision


class MockBall:
    def __init__(self, hp=100, max_hp=100):
        self.hp = hp
        self.max_hp = max_hp
        self.ball_type = "neural"
        self.nn_weights = None
        self.nn_biases = None
        self.skill_timer = 0.0
        self.difficulty = "medium"
        self.current_action = None

    def get_hp_percent(self):
        return self.hp / self.max_hp


class MockWorld:
    def __init__(self):
        self.entities = {
            "enemies": [],
            "allies": [],
            "boosters": [],
        }

    def get_nearby_entities(self, ball, radius):
        return self.entities


def test_neural_decision():
    ball = MockBall()
    world = MockWorld()

    # Create a small manual net
    # inputs: hp_percent, danger_level, opportunity_score, threat_level
    # outputs: 7 actions -> flee, defend, collect_booster, attack, chase, use_skill, kite
    ball.nn_weights = [
        [0.0, 10.0, 0.0, 0.0],  # flee: likes danger
        [0.0, 0.0, 0.0, 0.0],   # defend
        [0.0, 0.0, 10.0, 0.0],  # collect_booster: likes opportunity
        [0.0, 0.0, 0.0, 0.0],   # attack
        [0.0, 0.0, 0.0, 0.0],   # chase
        [0.0, 0.0, 0.0, 0.0],   # use_skill
        [0.0, 0.0, 0.0, 0.0],   # kite
    ]
    ball.nn_biases = [0.0] * 7

    nd = NeuralDecision(ball, world)

    # Test flee
    action = nd.choose_action({"danger_level": 1.0, "opportunity_score": 0.0}, "neutral")
    assert action == "flee"

    # Test collect_booster
    action = nd.choose_action({"danger_level": 0.0, "opportunity_score": 1.0}, "neutral")
    assert action == "collect_booster"

def test_neural_network_brain():
    ball = MockBall()
    world = MockWorld()

    # Make sure NeuralNetworkBrain injects NeuralDecision
    brain = NeuralNetworkBrain(ball, world)
    assert isinstance(brain.decision_layer, NeuralDecision)

    # Verify processing loop works and calls the decision layer
    ball.nn_weights = [
        [0.0, 0.0, 0.0, 0.0],   # flee
        [0.0, 0.0, 0.0, 0.0],   # defend
        [0.0, 0.0, 0.0, 0.0],   # collect_booster
        [10.0, 0.0, 0.0, 0.0],  # attack: likes high HP
        [0.0, 0.0, 0.0, 0.0],   # chase
        [0.0, 0.0, 0.0, 0.0],   # use_skill
        [0.0, 0.0, 0.0, 0.0],   # kite
    ]
    ball.nn_biases = [0.0] * 7

    # This should internally trigger the perception, emotion, and the decision
    # Attack should win because HP is 100% and weight for attack on HP is 10.0

    # Override action to just store the chosen strategy
    def mock_action(strategy, delta):
        ball.current_action = strategy

    brain.action = mock_action

    # Run a process cycle
    brain.process(0.1)

    assert ball.current_action == "attack"
