import json
import random
import os
import numpy as np
from typing import List, Dict, Any

class NeuralNet:
    def __init__(self, input_size: int, output_size: int):
        self.input_size = input_size
        self.output_size = output_size
        # Simple linear layer (weights + biases)
        # weights[i][j] is the weight from input j to output i
        self.weights = np.random.uniform(-1, 1, (output_size, input_size)).tolist()
        self.biases = np.random.uniform(-1, 1, output_size).tolist()

    def predict(self, inputs: List[float]) -> List[float]:
        """Forward pass."""
        if len(inputs) != self.input_size:
            # Fallback or truncate/pad if mismatch
            inputs = (inputs + [0.0]*self.input_size)[:self.input_size]

        inputs_np = np.array(inputs)
        weights_np = np.array(self.weights)
        biases_np = np.array(self.biases)
        outputs_np = weights_np.dot(inputs_np) + biases_np
        return outputs_np.tolist()

    def mutate(self, rate: float = 0.1, amount: float = 0.5) -> None:
        """Randomly adjust weights and biases for genetic algorithm using numpy."""
        weights_np = np.array(self.weights)
        biases_np = np.array(self.biases)

        # Mutate biases
        bias_mask = np.random.rand(self.output_size) < rate
        bias_mutations = np.random.uniform(-amount, amount, self.output_size)
        biases_np[bias_mask] += bias_mutations[bias_mask]

        # Mutate weights
        weight_mask = np.random.rand(self.output_size, self.input_size) < rate
        weight_mutations = np.random.uniform(-amount, amount, (self.output_size, self.input_size))
        weights_np[weight_mask] += weight_mutations[weight_mask]

        self.weights = weights_np.tolist()
        self.biases = biases_np.tolist()

    def clone(self) -> 'NeuralNet':
        """Create a deep copy of this network."""
        new_net = NeuralNet(self.input_size, self.output_size)
        new_net.weights = [row[:] for row in self.weights]
        new_net.biases = self.biases[:]
        return new_net

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "input_size": self.input_size,
            "output_size": self.output_size,
            "weights": self.weights,
            "biases": self.biases
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NeuralNet':
        """Deserialize from dictionary."""
        nn = cls(data["input_size"], data["output_size"])
        nn.weights = data["weights"]
        nn.biases = data["biases"]
        return nn

    def save(self, filepath: str) -> None:
        """Save network to JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f)

    def load(self, filepath: str) -> bool:
        """Load network from JSON file. Returns True if successful."""
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
            self.input_size = data["input_size"]
            self.output_size = data["output_size"]
            self.weights = data["weights"]
            self.biases = data["biases"]
            return True
        return False
