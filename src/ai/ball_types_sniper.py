"""
Auto-generated ball type: Sniper
Long range killer, high damage, low HP
"""

from typing import Any


class Sniper:
    BALL_TYPE = "sniper"
    HP = 60
    SPEED = 1.5
    DAMAGE = 35
    RADIUS = 9
    PERCEPTION_RADIUS = 500
    AGGRESSION = 0.6
    COLOR = "blue"
    SKILL = "precision_shot"
    SKILL_COOLDOWN = 6.0

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
        self.personality = "sniper"

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
