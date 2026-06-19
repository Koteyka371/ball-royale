import os
import json
from typing import Any, Dict


class NeuralDecision:
    """
    Neural Decision system that evaluates options and chooses an action.
    Uses neural network weights and biases directly injected into the ball.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def choose_action(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        # 1. Extract inputs
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp") and getattr(self.ball, "max_hp", 0) > 0:
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        danger_level = perception_data.get("danger_level", 0.0)
        opportunity_score = perception_data.get("opportunity_score", 0.0)
        threat_level = perception_data.get("threat_level", 0.0)

        inputs = [hp_percent, danger_level, opportunity_score, threat_level]

        # 2. Extract weights
        weights = getattr(self.ball, "nn_weights", None)
        biases = getattr(self.ball, "nn_biases", None)

        if weights is None or biases is None:
            # Try to load them if not injected by trainer
            filepath = os.path.join(os.path.dirname(__file__), "nn_weights.json")
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        weights = data["weights"]
                        biases = data["biases"]
                        # Cache them
                        self.ball.nn_weights = weights
                        self.ball.nn_biases = biases
                except Exception:
                    pass

        # Fallback to idle if load fails
        if weights is None or biases is None:
            return "idle"

        # 3. Predict
        actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "group_attack"]
        best_score = -9999.0
        best_action = "idle"

        for i, action in enumerate(actions):
            if i < len(biases):
                score = biases[i]
                for j in range(len(inputs)):
                    if i < len(weights) and j < len(weights[i]):
                        score += inputs[j] * weights[i][j]
                if score > best_score:
                    best_score = score
                    best_action = action

        # Additional checks
        skill_timer = getattr(self.ball, "skill_timer", 0.0)
        if best_action == "use_skill" and skill_timer > 0:
            return "chase"  # Fallback

        return best_action
