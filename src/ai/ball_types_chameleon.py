"""
Auto-generated ball type: Chameleon

Blends into the background color or nearest wall when standing still, reducing perception radius and hiding from minimap.
"""

import math
from ai.personality import Personality

class Chameleon:
    BALL_TYPE = "chameleon"
    HP = 90
    SPEED = 7.0
    DAMAGE = 25
    RADIUS = 8
    PERCEPTION_RADIUS = 350
    AGGRESSION = 0.8
    COLOR = "black"
    SKILL = "blend"
    SKILL_COOLDOWN = 4.0
    ATTACK_RANGE = 21.0

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
        self.attack_timer = 0.0
        self.attack_range = float(self.ATTACK_RANGE)
        self.personality = Personality("cunning")
        self.blend_amount = 0.0
        self.invisible_to_minimap = False

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
        dist_sq = dx * dx + dy * dy
        if dist_sq > 0.0001:
            dist = math.sqrt(dist_sq)
            nx = dx / dist
            ny = dy / dist
            step = self.SPEED * delta * 60.0

            speed_mult = getattr(self, "speed_multiplier", 1.0)
            self.x += nx * min(step * speed_mult, dist)
            self.y += ny * min(step * speed_mult, dist)

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
        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
