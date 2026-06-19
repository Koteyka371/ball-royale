"""
Auto-generated ball type: Neural
A ball controlled by a simple neural network skill: numpy, no external libs
"""

from typing import Any, List


class Neural:
    BALL_TYPE = "neural"
    HP = 100
    SPEED = 2.0
    DAMAGE = 10
    RADIUS = 10
    PERCEPTION_RADIUS = 200
    AGGRESSION = 0.5
    COLOR = "purple"
    SKILL = "neural_predict"
    SKILL_COOLDOWN = 5.0

    def __init__(self, ball_id: int, x: float = 0.0, y: float = 0.0):
        self.id = ball_id
        self.hp = self.HP
        self.max_hp = self.HP
        self.x = x
        self.y = y
        self.alive = True
        self.kills = 0
        self.current_action = "idle"
        self.skill_timer = 0.0
        self.personality = "neural"

        # Simple Neural Network state
        self.weights = [[0.1, -0.2], [-0.1, 0.3]]
        self.biases = [0.5, -0.1]
        self.last_prediction = []

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float) -> None:
        self.current_action = "flee"

    def attack(self, delta: float) -> None:
        self.current_action = "attack"

    def defend(self, delta: float) -> None:
        self.current_action = "defend"

    def collect_booster(self, delta: float) -> None:
        self.current_action = "opportunistic"

    def idle(self, delta: float) -> None:
        self.current_action = "idle"

    def take_damage(self, amount: float) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN

            # Use dot product to emulate a neural predict step
            inputs = [self.get_hp_percent(), self.kills]
            self.last_prediction = self._neural_predict(inputs)

            # Use prediction to control the ball
            if self.last_prediction:
                if self.last_prediction[0] > self.last_prediction[1]:
                    self.attack(0.016)
                else:
                    self.flee(0.016)

            return True
        return False

    def _neural_predict(self, inputs: List[float]) -> List[float]:
        """Simple matrix multiplication (dot product) to emulate neural network prediction."""
        if not inputs:
            return []

        outputs = []
        for i in range(len(self.weights)):
            score = self.biases[i]
            for j in range(len(inputs)):
                # Ensure we don't index out of bounds
                weight = self.weights[i][j] if j < len(self.weights[i]) else 0.0
                score += inputs[j] * weight
            outputs.append(score)
        return outputs

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
