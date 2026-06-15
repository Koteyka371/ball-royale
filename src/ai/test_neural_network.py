import os
import json
import pytest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.ai.neural_network import NeuralNetwork

def test_neural_network_initialization():
    nn = NeuralNetwork(5, 8, 7)
    assert nn.input_size == 5
    assert nn.hidden_size == 8
    assert nn.output_size == 7

    weights = nn.get_weights()
    assert len(weights["weights_ih"]) == 8
    assert len(weights["weights_ih"][0]) == 5
    assert len(weights["weights_ho"]) == 7
    assert len(weights["weights_ho"][0]) == 8
    assert len(weights["bias_h"]) == 8
    assert len(weights["bias_o"]) == 7

def test_neural_network_predict():
    nn = NeuralNetwork(5, 8, 7)
    inputs = [1.0, 0.5, -0.5, 0.0, 1.0]
    outputs = nn.predict(inputs)

    assert len(outputs) == 7
    # Sigmoid output should be between 0 and 1
    for out in outputs:
        assert 0.0 <= out <= 1.0

def test_neural_network_predict_invalid_input():
    nn = NeuralNetwork(5, 8, 7)
    with pytest.raises(ValueError):
        nn.predict([1.0, 0.5]) # Wrong size

def test_neural_network_mutate():
    nn = NeuralNetwork(5, 8, 7)
    initial_weights = nn.get_weights()

    # Mutate with high rate to ensure change
    nn.mutate(1.0)
    mutated_weights = nn.get_weights()

    # Check that at least some weights changed
    changed = False
    for i in range(8):
        for j in range(5):
            if initial_weights["weights_ih"][i][j] != mutated_weights["weights_ih"][i][j]:
                changed = True
                break
    assert changed

def test_neural_network_reinforce():
    nn = NeuralNetwork(5, 8, 7)
    inputs = [1.0, 0.5, -0.5, 0.0, 1.0]

    # Run predict to set last_inputs and last_hidden
    initial_outputs = nn.predict(inputs)
    initial_prob = initial_outputs[2]

    # Reinforce action index 2 positively
    nn.reinforce(2, reward=10.0, learning_rate=0.1)

    # Run predict again
    new_outputs = nn.predict(inputs)
    new_prob = new_outputs[2]

    # Probability should increase
    assert new_prob > initial_prob

    # Reinforce negatively
    nn.reinforce(2, reward=-10.0, learning_rate=0.1)
    final_outputs = nn.predict(inputs)
    assert final_outputs[2] < new_prob

def test_neural_network_save_load(tmpdir):
    filepath = os.path.join(tmpdir, "test_weights.json")

    nn1 = NeuralNetwork(5, 8, 7)
    # Set a specific weight to test
    nn1.weights_ih[0][0] = 9.99
    nn1.save(filepath)

    assert os.path.exists(filepath)

    nn2 = NeuralNetwork(5, 8, 7)
    success = nn2.load(filepath)

    assert success
    assert nn2.weights_ih[0][0] == 9.99
