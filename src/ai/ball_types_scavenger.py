"""
Auto-generated ball type: Scavenger
"""

import math
from ai.personality import Personality

class Scavenger:
    BALL_TYPE = "scavenger"
    HP = 90
    SPEED = 2.0
    DAMAGE = 8
    RADIUS = 10
    PERCEPTION_RADIUS = 150
    AGGRESSION = 0.5
    COLOR = 'orange'
    SKILL = 'dash'
    SKILL_COOLDOWN = 6.0

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
        self.materials_collected = 0
        self.ball_type = "scavenger"
        self.damage = float(self.DAMAGE)
        self.speed = float(self.SPEED)
        self.personality = Personality("opportunistic")

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float, target=None) -> None:
        self.current_action = "flee"
