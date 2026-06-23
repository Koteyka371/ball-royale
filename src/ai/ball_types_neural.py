"""
Auto-generated ball type: Neural
A ball controlled by a simple neural network.
"""


from ai.personality import Personality
import random


class NumpyArray:
    def __init__(self, data):
        self.data = data

    def dot(self, other):
        if isinstance(self.data[0], list):
            # Matrix-vector multiplication
            # self.data is (N, M), other.data is (M,)
            result = []
            for row in self.data:
                dot_prod = sum(a * b for a, b in zip(row, other.data))
                result.append(dot_prod)
            return NumpyArray(result)
        else:
            # Vector-vector dot product
            return sum(a * b for a, b in zip(self.data, other.data))

    def __add__(self, other):
        if isinstance(other, NumpyArray):
            return NumpyArray([a + b for a, b in zip(self.data, other.data)])
        elif isinstance(other, list):
            return NumpyArray([a + b for a, b in zip(self.data, other)])
        return self

    def argmax(self):
        return self.data.index(max(self.data))

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

        # Simple neural network using numpy
        self.input_size = 4
        self.output_size = 3 # example: attack, flee, idle

        self.weights = [[random.uniform(-1, 1) for _ in range(self.output_size)] for _ in range(self.input_size)]
        self.biases = [random.uniform(-1, 1) for _ in range(self.output_size)]

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

            # Predict next action using pure python
            inputs = [self.get_hp_percent(), self.AGGRESSION, float(self.kills), self.skill_timer]

            # Forward pass using our pure-python NumpyArray
            # self.weights is shape (input_size, output_size)
            # Transpose weights to (output_size, input_size) for easier multiplication
            w_T = [[self.weights[i][j] for i in range(self.input_size)] for j in range(self.output_size)]

            inputs_arr = NumpyArray(inputs)
            weights_arr = NumpyArray(w_T)

            outputs_arr = weights_arr.dot(inputs_arr) + self.biases

            # argmax
            action_idx = outputs_arr.argmax()
            actions = ["attack", "flee", "idle"]
            self.current_action = actions[action_idx]

            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
