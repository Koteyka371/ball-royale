import pytest
from src.ai.nn import NeuralNetwork
from src.ai.neural_network_brain import NeuralNetworkBrain

def test_nn_initialization():
    nn = NeuralNetwork(input_size=4, hidden_size=8, output_size=6)
    weights = nn.get_weights()
    assert len(weights["weights_ih"]) == 8
    assert len(weights["weights_ih"][0]) == 4
    assert len(weights["bias_h"]) == 8
    assert len(weights["weights_ho"]) == 6
    assert len(weights["weights_ho"][0]) == 8
    assert len(weights["bias_o"]) == 6

def test_nn_feedforward():
    nn = NeuralNetwork(input_size=4, hidden_size=8, output_size=6)
    inputs = [1.0, 0.5, 0.0, 1.0]
    outputs = nn.feedforward(inputs)
    assert len(outputs) == 6

def test_nn_brain_evaluate():
    brain = NeuralNetworkBrain()
    action = brain.evaluate(hp_percent=0.5, danger_level=0.8, opportunity_score=0.1, threat_level=0.9)
    assert action in ["flee", "defend", "collect_booster", "attack", "chase", "use_skill"]

def test_nn_brain_with_weights():
    nn = NeuralNetwork(input_size=4, hidden_size=8, output_size=6)
    weights = nn.get_weights()

    brain = NeuralNetworkBrain(nn_weights=weights)
    action = brain.evaluate(hp_percent=1.0, danger_level=0.0, opportunity_score=1.0, threat_level=0.0)
    assert action in ["flee", "defend", "collect_booster", "attack", "chase", "use_skill"]
