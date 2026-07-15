"""
Neural Ball Implementation
A ball controlled by a simple neural network using a custom numpy-like array implementation.
No external libraries are used as per requirements.
"""
import os
from ai.personality import Personality
import random
from typing import List, Tuple, Union, Any

class NumpyArray:
    """
    A pure Python matrix abstraction implemented completely from scratch.
    Provides numpy-like behavior including matrix multiplication, dot product,
    element-wise addition, relu activation, and argmax.
    """
    def __init__(self, data: Union[List[float], List[List[float]]]):
        self._data: List[Any] = list(data)
        if not data:
            self.shape: Tuple[int, ...] = (0,)
        elif isinstance(data[0], list):
            self.shape = (len(data), len(data[0]))
        else:
            self.shape = (len(data),)

    def matmul(self, other: 'NumpyArray') -> 'NumpyArray':
        """Performs matrix multiplication."""
        if len(self.shape) == 2 and len(other.shape) == 2 and self.shape[1] == other.shape[0]:
            result = [[0.0 for _ in range(other.shape[1])] for _ in range(self.shape[0])]
            for i in range(self.shape[0]):
                for j in range(other.shape[1]):
                    for k in range(self.shape[1]):
                        result[i][j] += self._data[i][k] * other._data[k][j]
            return NumpyArray(result)
        raise ValueError("Unsupported matmul shapes")

    def dot(self, other: 'NumpyArray') -> 'NumpyArray':
        """Performs dot product for 1D . 2D."""
        if len(self.shape) == 1 and len(other.shape) == 2:
            result = [0.0] * other.shape[1]
            for j in range(other.shape[1]):
                dot_prod = 0.0
                for i in range(self.shape[0]):
                    dot_prod += self._data[i] * other._data[i][j]
                result[j] = dot_prod
            return NumpyArray(result)
        raise ValueError("Unsupported dot product shapes")

    def __add__(self, other: 'NumpyArray') -> 'NumpyArray':
        """Element-wise addition."""
        if len(self.shape) == 1 and len(other.shape) == 1:
            return NumpyArray([float(self._data[i]) + float(other._data[i]) for i in range(self.shape[0])])
        raise ValueError("Unsupported add shapes")

    def relu(self) -> 'NumpyArray':
        """Applies ReLU activation."""
        if len(self.shape) == 1:
            return NumpyArray([max(0.0, float(x)) for x in self._data])
        raise ValueError("Unsupported relu shape")

    def argmax(self) -> int:
        """Returns the index of the maximum value."""
        float_data = [float(x) for x in self._data]
        max_val = max(float_data)
        return float_data.index(max_val)


class Neural:
    """
    Neural Ball class.
    Uses the custom NumpyArray to process inputs and make decisions.
    Evaluates HP, aggression, kills, and skill cooldown to choose an action.
    """
    BALL_TYPE = "neural"
    HP = 100
    SPEED = 4.5
    DAMAGE = 15
    RADIUS = 10
    PERCEPTION_RADIUS = 300
    AGGRESSION = 0.5
    COLOR = "purple"
    SKILL_COOLDOWN = 4.0

    def __init__(self, ball_id: int, x: float = 0.0, y: float = 0.0, skill: str = None):
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
        self.SKILL = skill if skill else random.choice(["dash", "shield", "heal"])
        self.personality = Personality("analytical")

        # Neural Network architecture
        self.input_size = 4
        config_path = os.path.join(os.path.dirname(__file__), "..", "ui", "neural_config.json")
        if os.path.exists(config_path):
            try:
                import json
                with open(config_path, "r") as f:
                    data = json.load(f)
                    if "neural_inputs" in data:
                        self.input_size = len(data["neural_inputs"])
            except Exception:
                pass
        self.output_size = 4
        self.hidden_size = 5

        # Initialize weights and biases randomly between -1 and 1
        self.hidden_weights = NumpyArray([[random.uniform(-1, 1) for _ in range(self.hidden_size)] for _ in range(self.input_size)])
        self.hidden_biases = NumpyArray([random.uniform(-1, 1) for _ in range(self.hidden_size)])

        self.output_weights = NumpyArray([[random.uniform(-1, 1) for _ in range(self.output_size)] for _ in range(self.hidden_size)])
        self.output_biases = NumpyArray([random.uniform(-1, 1) for _ in range(self.output_size)])

    def get_hp_percent(self) -> float:
        """Returns current HP as a percentage."""
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
        if getattr(self, "radiation_duration", 0.0) > 0:
            amount *= getattr(self, "radiation_multiplier", 1.5)

        """Handles taking damage."""
        if self.hp == self.max_hp and amount > 0:
            self.first_hit_taken = True
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        """
        Sets the current action to use the equipped skill.
        """
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN
            self.current_action = "use_skill"
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
