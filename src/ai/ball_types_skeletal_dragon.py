"""
Auto-generated ball type: Skeletal Dragon
"""

import math
from ai.personality import Personality

class SkeletalDragon:
    BALL_TYPE = "skeletal_dragon"
    HP = 150
    SPEED = 3.5
    DAMAGE = 25
    RADIUS = 15
    PERCEPTION_RADIUS = 500
    AGGRESSION = 0.8
    COLOR = "dark_green"

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
        self.attack_timer = 0.0
        self.attack_range = 150.0
        self.personality = Personality("aggressive")
        self.has_ranged_breath = True
        self.is_enraged = True
        self.enrage_timer = 99999.0
        self.dragon_breath_timer = 0.0

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float, target=None) -> None:
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

            if dist > self.attack_range * 0.8:
                self.x += nx * min(step, dist)
                self.y += ny * min(step, dist)

            if dist <= self.attack_range:
                if self.attack_timer <= 0:
                    self.attack_timer = 1.5
                    world = getattr(self, "world", None)
                    if not world and hasattr(self, "_cached_world"):
                        world = self._cached_world

                    if world and hasattr(world, "projectiles"):
                        proj_id = len(world.projectiles) + 1000
                        # Standard object creation for projectile (using type to avoid defining a class if not needed)
                        proj = type('GenericProjectile', (), {})()
                        proj.id = proj_id
                        proj.x = self.x
                        proj.y = self.y
                        proj.vx = nx * 300
                        proj.vy = ny * 300
                        proj.radius = 8.0
                        proj.hp = 1
                        proj.alive = True
                        proj.active = True
                        proj.ball_type = "projectile"

                        world.projectiles.append(proj)

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

    def tick(self, delta: float) -> None:
        if not self.alive:
            return
        if self.attack_timer > 0:
            self.attack_timer -= delta

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp}"
