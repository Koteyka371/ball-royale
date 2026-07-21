import math
from ai.personality import Personality

class Linker:
    BALL_TYPE = "linker"
    HP = 100
    SPEED = 5.0
    DAMAGE = 2
    RADIUS = 12
    PERCEPTION_RADIUS = 250
    AGGRESSION = 0.5
    COLOR = 'blue'
    SKILL = 'none'
    SKILL_COOLDOWN = 10.0

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
        self.personality = Personality("aggressive")
        self.link_target = None

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def take_damage(self, amount: float) -> None:
        if getattr(self, "radiation_duration", 0.0) > 0:
            amount *= getattr(self, "radiation_multiplier", 1.5)

        if self.link_target is not None and getattr(self.link_target, "alive", True):
            shared_amount = amount * 0.5
            self.link_target.hp -= shared_amount
            if self.link_target.hp <= 0:
                self.link_target.hp = 0.0
                self.link_target.alive = False
            amount -= shared_amount

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
