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
        self.configured_inputs = ["hp_percent", "danger_level", "opportunity_score", "threat_level"]
        config_path = os.path.join(os.path.dirname(__file__), "..", "ui", "neural_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    if "neural_inputs" in data:
                        self.configured_inputs = data["neural_inputs"]
            except Exception:
                pass

    def choose_action(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        # 1. Extract inputs
        inputs = []
        for input_name in getattr(self, "configured_inputs", ["hp_percent", "danger_level", "opportunity_score", "threat_level", "distance_to_zone"]):
            if input_name == "hp_percent":
                val = 1.0
                if hasattr(self.ball, "get_hp_percent"):
                    val = self.ball.get_hp_percent()
                elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp") and getattr(self.ball, "max_hp", 0) > 0:
                    val = float(self.ball.hp) / float(self.ball.max_hp)
                inputs.append(val)
            elif input_name == "danger_level":
                inputs.append(perception_data.get("danger_level", 0.0))
            elif input_name == "opportunity_score":
                inputs.append(perception_data.get("opportunity_score", 0.0))
            elif input_name == "threat_level":
                inputs.append(perception_data.get("threat_level", 0.0))
            elif input_name == "nearest_enemy_distance":
                enemies = perception_data.get("enemies", [])
                val = 1000.0
                if enemies and hasattr(self.ball, "x") and hasattr(self.ball, "y"):
                    val = min((((e.x - self.ball.x)**2 + (e.y - self.ball.y)**2)**0.5 for e in enemies if hasattr(e, "x") and hasattr(e, "y")), default=1000.0)
                inputs.append(val)
            elif input_name == "distance_to_zone":
                # Compute distance to moving zone center if in MovingZone mode, else default
                val = 1000.0
                game_mode = getattr(self.world, "game_mode", None)
                if game_mode and getattr(game_mode, "name", "") == "Moving Zone":
                    zone_x = getattr(game_mode, "zone_x", 500)
                    zone_y = getattr(game_mode, "zone_y", 500)
                    if hasattr(self.ball, "x") and hasattr(self.ball, "y"):
                        val = ((self.ball.x - zone_x)**2 + (self.ball.y - zone_y)**2)**0.5
                inputs.append(val)
            elif input_name == "number_of_allies":
                inputs.append(float(len(perception_data.get("allies", []))))
            elif input_name == "boss_hp":
                val = 0.0
                enemies = perception_data.get("enemies", [])
                bosses = [e for e in enemies if getattr(e, "ball_type", "") == "juggernaut"]
                if bosses:
                    val = float(getattr(bosses[0], "hp", 0.0))
                inputs.append(val)
            elif input_name == "map_hazard_distance":
                traps = perception_data.get("traps", [])
                val = 1000.0
                if traps and hasattr(self.ball, "x") and hasattr(self.ball, "y"):
                    val = min((((t.x - self.ball.x)**2 + (t.y - self.ball.y)**2)**0.5 for t in traps if hasattr(t, "x") and hasattr(t, "y")), default=1000.0)
                inputs.append(val)
            elif input_name == "skill_dash":
                inputs.append(1.0 if getattr(self.ball, "SKILL", "") == "dash" else 0.0)
            elif input_name == "skill_shield":
                inputs.append(1.0 if getattr(self.ball, "SKILL", "") == "shield" else 0.0)
            elif input_name == "skill_heal":
                inputs.append(1.0 if getattr(self.ball, "SKILL", "") == "heal" else 0.0)
            else:
                inputs.append(0.0)

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
        actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "group_attack", "hide_behind", "hold_zone"]
        best_score = -9999.0
        best_action = "idle"

        # Use pure Python for prediction
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
