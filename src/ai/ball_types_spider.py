"""
Auto-generated ball type: Spider
Attaches to boundaries, avoids center, drops web-mines.
"""

import math
from ai.personality import Personality

class Spider:
    BALL_TYPE = "spider"
    HP = 80
    SPEED = 4.0
    DAMAGE = 20
    RADIUS = 9
    PERCEPTION_RADIUS = 300
    AGGRESSION = 0.5
    COLOR = "black"

    def __init__(self, ball_id: int, x: float = 0.0, y: float = 0.0):
        self.id = ball_id
        self.hp = float(self.HP)
        self.max_hp = float(self.HP)
        self.x = x
        self.y = y
        self.alive = True
        self.kills = 0
        self.current_action = "idle"
        self.web_drop_timer = 0.0
        self.first_hit_taken = False
        self.personality = Personality("cautious")

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float) -> None:
        self.current_action = "wall_crawl"

    def attack(self, delta: float) -> None:
        self.current_action = "wall_crawl"

    def defend(self, delta: float) -> None:
        self.current_action = "wall_crawl"

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

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
