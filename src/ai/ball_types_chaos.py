import math
import random
from ai.personality import Personality

class Chaos:
    BALL_TYPE = "chaos"
    HP = 100
    SPEED = 3.0
    DAMAGE = 15
    RADIUS = 10
    PERCEPTION_RADIUS = 250
    AGGRESSION = 0.5
    COLOR = "magenta"
    SKILL = "chaos_link"
    SKILL_COOLDOWN = 2.0

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
        self.difficulty = "chaos"
        self.personality = Personality("chaotic")

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float) -> None:
        self.current_action = "flee"

    def attack(self, delta: float, target=None) -> None:
        self.current_action = "attack"
        if target is None:
            return

        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)

        if dist > 0.0001:
            # chaotic movement
            nx = dx / dist + (random.random() - 0.5) * 0.5
            ny = dy / dist + (random.random() - 0.5) * 0.5

            n_dist = math.hypot(nx, ny)
            if n_dist > 0.0001:
                nx /= n_dist
                ny /= n_dist

            step = self.SPEED * delta * 60.0

            self.x += nx * min(step, dist)
            self.y += ny * min(step, dist)

        if dist < (self.RADIUS + getattr(target, 'radius', 10.0) + 5.0) and self.skill_timer <= 0:
            self.use_skill()

    def defend(self, delta: float) -> None:
        self.current_action = "defend"

    def collect_booster(self, delta: float) -> None:
        self.current_action = "opportunistic"

    def idle(self, delta: float) -> None:
        self.current_action = "idle"

    def take_damage(self, amount: float) -> None:
        if getattr(self, "radiation_duration", 0.0) > 0:
            amount *= getattr(self, "radiation_multiplier", 1.5)

        if self.hp == self.max_hp and amount > 0:
            self.first_hit_taken = True
        self.hp -= amount

        if self.hp <= 0 and getattr(self, "quantum_relay_timer", 0.0) > 0.0:
            self.hp = self.max_hp * 0.2
            self.x = getattr(self, "quantum_relay_x", self.x)
            self.y = getattr(self, "quantum_relay_y", self.y)
            self.quantum_relay_timer = 0.0
            if hasattr(self, "world") and hasattr(self.world, "events"):
                self.world.events.append({"type": "quantum_relay_triggered", "x": self.x, "y": self.y})
            return

        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
