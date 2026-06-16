from typing import Any, Dict, List
from .nn import NeuralNetwork

class NeuralNetworkBrain:
    """
    Evaluates actions using a neural network.
    """

    ACTIONS = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill"]

    def __init__(self, nn_weights: Dict[str, Any] = None):
        # 4 inputs: hp_percent, danger_level, opportunity_score, threat_level
        # 8 hidden nodes
        # 6 outputs: corresponding to self.ACTIONS
        self.nn = NeuralNetwork(input_size=4, hidden_size=8, output_size=6, weights_data=nn_weights)

    def evaluate(self, hp_percent: float, danger_level: float, opportunity_score: float, threat_level: float) -> str:
        inputs = [hp_percent, danger_level, opportunity_score, threat_level]
        outputs = self.nn.feedforward(inputs)

        best_score = -float('inf')
        best_action_index = 0

        for i in range(len(outputs)):
            if outputs[i] > best_score:
                best_score = outputs[i]
                best_action_index = i

        return self.ACTIONS[best_action_index]
