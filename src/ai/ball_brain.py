from typing import Any, Dict

from .perception import Perception
from .emotion import Emotion
from .decision import Decision
from .action import Action
from .neural_network import NeuralNetwork


class BallBrain:
    """
    Core AI system for balls.
    Processes information through 4 layers: Perception, Emotion, Decision, Action.
    """

    ACTIONS = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "idle"]

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world
        self.perception_layer = Perception(self.ball, self.world)
        self.emotion_layer = Emotion(self.ball, self.world)
        self.decision_layer = Decision(self.ball, self.world)
        self.action_layer = Action(self.ball, self.world)

        self.is_neural = getattr(self.ball, "ball_type", "") == "neural"
        if self.is_neural:
            self.nn = NeuralNetwork(input_size=5, hidden_size=8, output_size=7)
            if hasattr(self.ball, "nn_weights"):
                self.nn.set_weights(self.ball.nn_weights)
            else:
                if self.nn.load("src/ai/nn_weights.json"):
                    self.ball.nn_weights = self.nn.get_weights()

            self.last_hp = getattr(self.ball, "hp", 100)
            self.last_kills = getattr(self.ball, "kills", 0)

    def process(self, delta: float) -> None:
        """Main processing loop through the 4 layers."""
        perception_data = self.perception()
        emotion_state = self.emotion(perception_data)
        decision = self.decision(perception_data, emotion_state)

        if self.is_neural:
            # Dynamic live learning based on state changes
            current_hp = getattr(self.ball, "hp", 100)
            current_kills = getattr(self.ball, "kills", 0)

            reward = 0.0
            if current_kills > self.last_kills:
                reward += 10.0 # Reward for kill
            if current_hp < self.last_hp:
                reward -= 1.0 # Penalty for taking damage

            if reward != 0.0:
                action_idx = self.ACTIONS.index(decision) if decision in self.ACTIONS else 6
                self.nn.reinforce(action_idx, reward, learning_rate=0.05)

            self.last_hp = current_hp
            self.last_kills = current_kills

        self.action(decision, delta)

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
        if self.is_neural:
            # Map perception to NN inputs
            hp_percent = 1.0
            if hasattr(self.ball, "get_hp_percent"):
                hp_percent = self.ball.get_hp_percent()
            elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
                hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

            inputs = [
                hp_percent,
                perception_data.get("danger_level", 0.0),
                perception_data.get("threat_level", 0.0),
                perception_data.get("opportunity_score", 0.0),
                1.0 if len(perception_data.get("enemies", [])) > 0 else 0.0
            ]

            outputs = self.nn.predict(inputs)

            # Find action with highest activation
            best_action_idx = 0
            best_activation = -1.0

            for i, activation in enumerate(outputs):
                if activation > best_activation:
                    best_activation = activation
                    best_action_idx = i

            return self.ACTIONS[best_action_idx]

        return self.decision_layer.choose_action(perception_data, emotion_state)

    def action(self, strategy: str, delta: float) -> None:
        """
        4. ACTION LAYER
        Delegates executing chosen strategy to the Action class.
        """
        self.action_layer.execute(strategy, delta)
