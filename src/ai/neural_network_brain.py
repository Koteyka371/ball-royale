from typing import Any, Dict

from .ball_brain import BallBrain
from .neural_decision import NeuralDecision


class NeuralNetworkBrain(BallBrain):
    """
    Neural Network wrapper that plugs into BallBrain architecture.
    Replaces the standard Decision layer with NeuralDecision to evaluate
    its performance against the standard Decision logic.
    """

    def __init__(self, ball: Any, world: Any):
        super().__init__(ball, world)
        # Override the decision layer with our new NeuralDecision
        self.decision_layer = NeuralDecision(self.ball, self.world)  # type: ignore

    def decision(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        """Explicitly override to ensure NeuralDecision is called."""
        return self.decision_layer.choose_action(perception_data, emotion_state)
