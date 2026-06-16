import math
import random
from typing import List, Dict, Any

class NeuralNetwork:
    """
    A simple feedforward neural network with one hidden layer.
    Uses ReLU for hidden layer activation and linear output.
    """

    def __init__(self, input_size: int, hidden_size: int, output_size: int, weights_data: Dict[str, Any] = None):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        if weights_data:
            self.weights_ih = weights_data["weights_ih"]
            self.bias_h = weights_data["bias_h"]
            self.weights_ho = weights_data["weights_ho"]
            self.bias_o = weights_data["bias_o"]
        else:
            self.weights_ih = [[random.uniform(-1.0, 1.0) for _ in range(input_size)] for _ in range(hidden_size)]
            self.bias_h = [random.uniform(-1.0, 1.0) for _ in range(hidden_size)]
            self.weights_ho = [[random.uniform(-1.0, 1.0) for _ in range(hidden_size)] for _ in range(output_size)]
            self.bias_o = [random.uniform(-1.0, 1.0) for _ in range(output_size)]

    def relu(self, x: float) -> float:
        return max(0.0, x)

    def feedforward(self, inputs: List[float]) -> List[float]:
        # Hidden layer
        hidden = []
        for i in range(self.hidden_size):
            sum_val = self.bias_h[i]
            for j in range(self.input_size):
                sum_val += inputs[j] * self.weights_ih[i][j]
            hidden.append(self.relu(sum_val))

        # Output layer
        outputs = []
        for i in range(self.output_size):
            sum_val = self.bias_o[i]
            for j in range(self.hidden_size):
                sum_val += hidden[j] * self.weights_ho[i][j]
            outputs.append(sum_val)

        return outputs

    def get_weights(self) -> Dict[str, Any]:
        return {
            "weights_ih": self.weights_ih,
            "bias_h": self.bias_h,
            "weights_ho": self.weights_ho,
            "bias_o": self.bias_o
        }
