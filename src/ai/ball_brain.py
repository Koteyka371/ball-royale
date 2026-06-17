import random
from typing import Any, Dict

from .perception import Perception
from .emotion import Emotion
from .decision import Decision
from .action import Action


class BallBrain:
    """
    Core AI system for balls.
    Processes information through 4 layers: Perception, Emotion, Decision, Action.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world
        self.perception_layer = Perception(self.ball, self.world)
        self.emotion_layer = Emotion(self.ball, self.world)
        self.decision_layer = Decision(self.ball, self.world)
        self.action_layer = Action(self.ball, self.world)

        self._reaction_timer = 0.0
        self._current_decision = "idle"

    def process(self, delta: float) -> None:
        """Main processing loop through the 4 layers."""
        self._reaction_timer -= delta

        if self._reaction_timer <= 0:
            perception_data = self.perception()
            emotion_state = self.emotion(perception_data)

            # Use Neural Network if ball type is "neural" and override is not disabled
            import os
            b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
            if b_type == "neural" and not os.environ.get("DISABLE_NN_OVERRIDE"):
                decision = self._neural_decision(perception_data)
            else:
                decision = self.decision(perception_data, emotion_state)

            self._current_decision = decision

            difficulty = getattr(self.ball, "difficulty", "medium")
            if difficulty == "easy":
                self._reaction_timer = 0.5
            elif difficulty == "medium":
                self._reaction_timer = 0.1
            elif difficulty == "hard":
                self._reaction_timer = 0.0
            elif difficulty == "chaos":
                self._reaction_timer = random.uniform(0.0, 0.2)
            else:
                self._reaction_timer = 0.1

        self.action(self._current_decision, delta)

    def perception(self) -> Dict[str, Any]:
        """
        1. PERCEPTION LAYER
        Delegates scanning the environment to the Perception class.
        """
        return self.perception_layer.scan()

    def emotion(self, perception_data: Dict[str, Any]) -> str:
        """
        2. EMOTION LAYER
        Delegates determining current emotional state to the Emotion class.
        """
        return self.emotion_layer.get_state(perception_data)

    def decision(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        """
        3. DECISION LAYER
        Chooses strategy based on perception and emotion.
        """
        return self.decision_layer.choose_action(perception_data, emotion_state)

    def action(self, strategy: str, delta: float) -> None:
        """
        4. ACTION LAYER
        Delegates executing chosen strategy to the Action class.
        """
        self.action_layer.execute(strategy, delta)

    def _neural_decision(self, perception_data: Dict[str, Any]) -> str:
        """Alternative decision layer using Neural Network weights directly injected into the ball."""
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
            import json, os
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

        # Fallback to standard decision if load fails
        if weights is None or biases is None:
            return self.decision(perception_data, self.emotion(perception_data))

        # 3. Predict
        actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill"]
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
