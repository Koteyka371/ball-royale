"""
Auto-generated ball type: Chronos
Support ball, heals allies, avoids combat, controls time
"""

from ai.personality import Personality

class Chronos:
    BALL_TYPE = "chronos"
    HP = 120
    SPEED = 5.0
    DAMAGE = 5
    RADIUS = 10
    PERCEPTION_RADIUS = 350
    AGGRESSION = 0.2
    COLOR = "purple"
    SKILL = "time_rewind"
    SKILL_COOLDOWN = 15.0

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
        self.damage = float(self.DAMAGE)
        self.personality = Personality("caring")
        self.state_history = []

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
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
