"""
Auto-generated ball type: Neural
A ball controlled by a simple neural network.
"""

from ai.personality import Personality
import random

class NumpyArray:
    """A pure python matrix abstraction."""
    def __init__(self, data):
        self.data = data
        if not data:
            self.shape = (0,)
        elif isinstance(data[0], list):
            self.shape = (len(data), len(data[0]))
        else:
            self.shape = (len(data),)

    def matmul(self, other):
        if len(self.shape) == 2 and len(other.shape) == 2 and self.shape[1] == other.shape[0]:
            result = [[0.0 for _ in range(other.shape[1])] for _ in range(self.shape[0])]
            for i in range(self.shape[0]):
                for j in range(other.shape[1]):
                    for k in range(self.shape[1]):
                        result[i][j] += self.data[i][k] * other.data[k][j]
            return NumpyArray(result)
        raise ValueError("Unsupported matmul shapes")

    def dot(self, other):
        if len(self.shape) == 1 and len(other.shape) == 2:
            result = [0.0] * other.shape[1]
            for j in range(other.shape[1]):
                dot_prod = 0.0
                for i in range(self.shape[0]):
                    dot_prod += self.data[i] * other.data[i][j]
                result[j] = dot_prod
            return NumpyArray(result)
        raise ValueError("Unsupported dot product shapes")

    def __add__(self, other):
        if len(self.shape) == 1 and len(other.shape) == 1:
            return NumpyArray([self.data[i] + other.data[i] for i in range(self.shape[0])])
        raise ValueError("Unsupported add shapes")

    def relu(self):
        if len(self.shape) == 1:
            return NumpyArray([max(0.0, x) for x in self.data])
        raise ValueError("Unsupported relu shape")

    def argmax(self):
        max_val = max(self.data)
        return self.data.index(max_val)

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
        self.input_size = 4
        self.output_size = 3
        self.hidden_size = 5
        self.hidden_weights = NumpyArray([[random.uniform(-1, 1) for _ in range(self.hidden_size)] for _ in range(self.input_size)])
        self.hidden_biases = NumpyArray([random.uniform(-1, 1) for _ in range(self.hidden_size)])
        self.output_weights = NumpyArray([[random.uniform(-1, 1) for _ in range(self.output_size)] for _ in range(self.hidden_size)])
        self.output_biases = NumpyArray([random.uniform(-1, 1) for _ in range(self.output_size)])

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
            inputs = NumpyArray([self.get_hp_percent(), self.AGGRESSION, float(self.kills), self.skill_timer])
            hidden = (inputs.dot(self.hidden_weights) + self.hidden_biases).relu()
            outputs = hidden.dot(self.output_weights) + self.output_biases
            action_idx = outputs.argmax()
            actions = ["attack", "flee", "idle"]
            self.current_action = actions[action_idx]
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
