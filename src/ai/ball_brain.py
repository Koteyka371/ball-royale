from typing import Any, Dict


from ai.perception import Perception

class BallBrain:
    """
    Core AI system for balls.
    Processes information through 4 layers: Perception, Emotion, Decision, Action.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world
        self.perception_system = Perception(self.ball, self.world)

    def process(self, delta: float) -> None:
        """Main processing loop through the 4 layers."""
        perception_data = self.perception()
        emotion_state = self.emotion(perception_data)
        decision = self.decision(perception_data, emotion_state)
        self.action(decision, delta)

    def perception(self) -> Dict[str, Any]:
        """
        1. PERCEPTION LAYER
        Delegates to the Perception class to scan environment and calculate levels.
        """
        return self.perception_system.scan()

    def emotion(self, perception_data: Dict[str, Any]) -> str:
        """
        2. EMOTION LAYER
        Determines current emotional state based on HP and situation.
        """
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        if hp_percent < 0.3:
            return "fear"

        if len(perception_data["boosters"]) > 0:
            return "greed"

        if hp_percent > 0.8 and len(perception_data["enemies"]) > 0:
            return "rage"

        return "neutral"

    def decision(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        """
        3. DECISION LAYER
        Chooses strategy based on perception and emotion.
        """
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        if hp_percent < 0.3 or emotion_state == "fear":
            return "flee"

        if perception_data["danger_level"] > 0.7:
            return "defend"

        if perception_data["opportunity_level"] > 0.5 or emotion_state == "greed":
            if len(perception_data["boosters"]) > 0:
                return "opportunistic"

        if len(perception_data["enemies"]) > 0:
            return "attack"

        personality = getattr(self.ball, "personality", "idle")
        return personality

    def action(self, strategy: str, delta: float) -> None:
        """
        4. ACTION LAYER
        Executes chosen strategy.
        """
        # Save the chosen strategy as current_action for testing
        self.ball.current_action = strategy

        if strategy == "flee":
            if hasattr(self.ball, "flee"):
                self.ball.flee(delta)
        elif strategy == "attack":
            if hasattr(self.ball, "attack"):
                self.ball.attack(delta)
        elif strategy == "defend":
            if hasattr(self.ball, "defend"):
                self.ball.defend(delta)
        elif strategy == "opportunistic":
            if hasattr(self.ball, "collect_booster"):
                self.ball.collect_booster(delta)
        else:
            if hasattr(self.ball, "idle"):
                self.ball.idle(delta)
