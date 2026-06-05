"""
Auto-generated ball type: Berserker
Maximum aggression, damage increases as HP drops
"""

from typing import Any


class Berserker:
    BALL_TYPE = "berserker"
    HP = 100
    SPEED = 2.2
    DAMAGE = 20
    RADIUS = 13
    PERCEPTION_RADIUS = 220
    AGGRESSION = 1.0
    COLOR = "crimson"
    SKILL = "rage_burst"
    SKILL_COOLDOWN = 5.5

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
        self.personality = "berserker"

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
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
