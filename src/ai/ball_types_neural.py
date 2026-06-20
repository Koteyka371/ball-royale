"""
Auto-generated ball type: Neural
A ball controlled by a simple neural network.
"""


from ai.personality import Personality
import numpy as np  # type: ignore

class Neural:
    BALL_TYPE = "neural"
    HP = 100
    SPEED = 4.5
    DAMAGE = 15
    RADIUS = 10
    PERCEPTION_RADIUS = 300
    AGGRESSION = 0.5
    COLOR = "purple"
    SKILL = "numpy"
    SKILL_COOLDOWN = 4.0

    def __init__(self, ball_id: int, x: float = 0.0, y: float = 0.0):
        self.id = ball_id
        self.hp = float(self.HP)
        self.max_hp = float(self.HP)
        self.x = x
        self.y = y
        self.alive = True
        self.kills = 0
        self.first_hit_taken = False
        self.current_action = "idle"
        self.skill_timer = 0.0
        self.personality = Personality("analytical")

        # Simple neural network with numpy
        self.input_size = 4
        self.output_size = 3 # example: attack, flee, idle

        self.weights = np.random.uniform(-1, 1, (self.input_size, self.output_size))
        self.biases = np.random.uniform(-1, 1, self.output_size)

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
        if self.hp == self.max_hp and amount > 0:
            self.first_hit_taken = True
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN

            # Predict next action using numpy neural net
            inputs = np.array([self.get_hp_percent(), self.AGGRESSION, float(self.kills), self.skill_timer])

            outputs = np.dot(inputs, self.weights) + self.biases

            action_idx = int(np.argmax(outputs))
            actions = ["attack", "flee", "idle"]
            self.current_action = actions[action_idx]

            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
