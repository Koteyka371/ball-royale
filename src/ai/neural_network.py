import json
import random
import math
import os
from typing import List, Dict, Any, Optional

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(min(x, 20.0), -20.0)))

def relu(x: float) -> float:
    return max(0.0, x)

class NeuralNetwork:
    """
    A simple, dependency-free feedforward neural network.
    Supports basic forward propagation, mutation (for Genetic Algorithm),
    and reinforcement (for dynamic live learning).
    """

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Initialize weights and biases randomly between -1 and 1
        self.weights_ih = [[random.uniform(-1, 1) for _ in range(input_size)] for _ in range(hidden_size)]
        self.bias_h = [random.uniform(-1, 1) for _ in range(hidden_size)]

        self.weights_ho = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(output_size)]
        self.bias_o = [random.uniform(-1, 1) for _ in range(output_size)]

        # Store last activation for reinforcement learning
        self.last_inputs: List[float] = []
        self.last_hidden: List[float] = []

    def predict(self, inputs: List[float]) -> List[float]:
        """Forward propagation"""
        if len(inputs) != self.input_size:
            raise ValueError(f"Expected {self.input_size} inputs, got {len(inputs)}")

        self.last_inputs = list(inputs)

        # Input to Hidden
        hidden = []
        for i in range(self.hidden_size):
            sum_val = self.bias_h[i]
            for j in range(self.input_size):
                sum_val += inputs[j] * self.weights_ih[i][j]
            hidden.append(relu(sum_val))

        self.last_hidden = list(hidden)

        # Hidden to Output
        outputs = []
        for i in range(self.output_size):
            sum_val = self.bias_o[i]
            for j in range(self.hidden_size):
                sum_val += hidden[j] * self.weights_ho[i][j]
            outputs.append(sigmoid(sum_val))

        return outputs

    def get_weights(self) -> Dict[str, Any]:
        """Return a dictionary representing the network weights"""
        return {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "weights_ih": self.weights_ih,
            "bias_h": self.bias_h,
            "weights_ho": self.weights_ho,
            "bias_o": self.bias_o
        }

    def set_weights(self, weights: Dict[str, Any]) -> None:
        """Set network weights from a dictionary"""
        if weights["input_size"] != self.input_size or weights["hidden_size"] != self.hidden_size or weights["output_size"] != self.output_size:
            # Re-initialize sizes if loading a different architecture
            self.input_size = weights["input_size"]
            self.hidden_size = weights["hidden_size"]
            self.output_size = weights["output_size"]

        self.weights_ih = weights["weights_ih"]
        self.bias_h = weights["bias_h"]
        self.weights_ho = weights["weights_ho"]
        self.bias_o = weights["bias_o"]

    def save(self, filepath: str) -> None:
        """Save weights to a JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.get_weights(), f, indent=2)

    def load(self, filepath: str) -> bool:
        """Load weights from a JSON file. Returns True if successful."""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'r') as f:
                weights = json.load(f)
            self.set_weights(weights)
            return True
        except Exception as e:
            print(f"Error loading neural network weights from {filepath}: {e}")
            return False

    def mutate(self, rate: float) -> None:
        """Randomly mutate weights and biases (for Genetic Algorithm)"""
        def mutate_value(val: float) -> float:
            if random.random() < rate:
                return val + random.gauss(0, 0.1) # Add small Gaussian noise
            return val

        self.weights_ih = [[mutate_value(w) for w in row] for row in self.weights_ih]
        self.bias_h = [mutate_value(b) for b in self.bias_h]
        self.weights_ho = [[mutate_value(w) for w in row] for row in self.weights_ho]
        self.bias_o = [mutate_value(b) for b in self.bias_o]

    def reinforce(self, action_index: int, reward: float, learning_rate: float = 0.01) -> None:
        """
        Simple reinforcement learning step.
        Nudges weights connected to the chosen action_index based on the reward.
        If reward > 0, increase probability of this action given last_inputs.
        If reward < 0, decrease probability.
        """
        if not self.last_inputs or not self.last_hidden:
            return

        # Nudge weights from hidden to output for the specific action
        for j in range(self.hidden_size):
            # Gradient is roughly reward * input_activation
            delta = learning_rate * reward * self.last_hidden[j]
            self.weights_ho[action_index][j] += delta

        # Nudge bias for the specific action
        self.bias_o[action_index] += learning_rate * reward

        # Nudge weights from input to hidden based on contribution to action
        for i in range(self.hidden_size):
            # Weight contribution to the chosen action
            ho_weight = self.weights_ho[action_index][i]
            for j in range(self.input_size):
                delta = learning_rate * reward * ho_weight * self.last_inputs[j]
                self.weights_ih[i][j] += delta

            self.bias_h[i] += learning_rate * reward * ho_weight
