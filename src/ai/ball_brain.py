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

    def process(self, delta: float) -> None:
        """Main processing loop through the 4 layers."""
        perception_data = self.perception()
        emotion_state = self.emotion(perception_data)
        decision = self.decision(perception_data, emotion_state)
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
        return self.decision_layer.choose_action(perception_data, emotion_state)

    def action(self, strategy: str, delta: float) -> None:
        """
        4. ACTION LAYER
        Delegates executing chosen strategy to the Action class.
        """
        self.action_layer.execute(strategy, delta)
