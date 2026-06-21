import json
import random
import os
from typing import List, Dict, Any

class NeuralNet:
    def __init__(self, input_size: int, output_size: int):
        self.input_size = input_size
        self.output_size = output_size
        # Simple linear layer (weights + biases)
        # weights[i][j] is the weight from input j to output i
        self.weights = [[random.uniform(-1, 1) for _ in range(input_size)] for _ in range(output_size)]
        self.biases = [random.uniform(-1, 1) for _ in range(output_size)]

    def predict(self, inputs: List[float]) -> List[float]:
        """Forward pass."""
        if len(inputs) != self.input_size:
            # Fallback or truncate/pad if mismatch
            inputs = (inputs + [0.0]*self.input_size)[:self.input_size]

        outputs = [0.0] * self.output_size
        for i in range(self.output_size):
            out = self.biases[i]
            for j in range(self.input_size):
                out += inputs[j] * self.weights[i][j]
            outputs[i] = out
        return outputs

    def mutate(self, rate: float = 0.1, amount: float = 0.5) -> None:
        """Randomly adjust weights and biases for genetic algorithm using numpy."""
        # Mutate biases
        for i in range(self.output_size):
            if random.random() < rate:
                self.biases[i] += random.uniform(-amount, amount)

        # Mutate weights
        for i in range(self.output_size):
            for j in range(self.input_size):
                if random.random() < rate:
                    self.weights[i][j] += random.uniform(-amount, amount)

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
