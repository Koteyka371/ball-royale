"""
Auto-generated ball type: Ninja

Cunning fighter, uses Stealth to approach, attacks from behind for critical, flees after attack
"""

import math
from ai.personality import Personality

class Ninja:
    BALL_TYPE = "ninja"
    HP = 90
    SPEED = 7.0
    DAMAGE = 25
    RADIUS = 8
    PERCEPTION_RADIUS = 350
    AGGRESSION = 0.8
    COLOR = "black"
    SKILL = "wall_jump"
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

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float) -> None:
        self.current_action = "flee"

    def attack(self, delta: float) -> None:
        self.current_action = "flank"

    def flank(self, delta: float, target=None) -> None:
        """Flank - moves behind target and attacks, uses stealth to close gap"""
        self.current_action = "flank"

        if target is None:
            return

        # Predict position behind target based on its velocity
        target_vx = getattr(target, "vx", 0.0)
        target_vy = getattr(target, "vy", 0.0)

        # If target is not moving much, fallback to a fixed facing
        if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
            target_vx = getattr(target, 'last_vx', 1.0)
            target_vy = getattr(target, 'last_vy', 0.0)
            if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
                target_vx, target_vy = 1.0, 0.0
        else:
            # Normalize velocity
            v_dist_sq = target_vx * target_vx + target_vy * target_vy
            if v_dist_sq > 0.0001:
                v_dist = math.sqrt(v_dist_sq)
                target_vx /= v_dist
                target_vy /= v_dist

        # Flank point is behind the target
        target_radius = getattr(target, 'radius', 10.0)
        flank_distance = target_radius * 2.0 + 20.0
        flank_x = target.x - target_vx * flank_distance
        flank_y = target.y - target_vy * flank_distance

        # Move towards flank point
        dx = flank_x - self.x
        dy = flank_y - self.y
        dist_sq = dx * dx + dy * dy
        if dist_sq > 0.0001:
            dist = math.sqrt(dist_sq)
            nx = dx / dist
            ny = dy / dist

            step = self.SPEED * delta * 60.0
            self.x += nx * min(step, dist)
            self.y += ny * min(step, dist)

        # Calculate direct distance to target for attack
        direct_dx = target.x - self.x
        direct_dy = target.y - self.y
        direct_dist_sq = direct_dx * direct_dx + direct_dy * direct_dy
        direct_dist = math.sqrt(direct_dist_sq) if direct_dist_sq > 0.0001 else 0.0

        # Attack range
        attack_range = self.attack_range
        if hasattr(target, "radius"):
            attack_range = self.RADIUS + target.radius + 5

        # Use skill (stealth) if closing the gap
        if self.skill_timer <= 0 and direct_dist > attack_range * 1.5:
            self.use_skill()

        # Attack when in range
        if direct_dist <= attack_range:
            if self.attack_timer <= 0:
                # Check if attacking from behind (dot product of direction to target and target's velocity)
                dot_product = 0.0
                if direct_dist > 0.0001:
                    ndx, ndy = direct_dx / direct_dist, direct_dy / direct_dist
                    dot_product = ndx * target_vx + ndy * target_vy

                is_critical = dot_product > 0.5

                # We do not actually deal damage directly in the ball class, we just set state/timers.
                # However, since the prompt specifies to implement explicit class behavior like distance calcs and damage dealing
                # similar to Sniper.kite (which actually relies on action.py to deal damage, wait Sniper.kite just sets attack_timer).
                # Actually action._flank relies on world._deal_damage which is not accessible here (no world ref).
                # Wait, the prompt says: "with a x3 damage multiplier if the attack comes from behind".
                # But Ninja class does not have access to 'world'.
                # Actually, Sniper doesn't deal damage in `kite` method either, it just sets the timer.
                # Let's adjust self.damage based on critical. Action layer will read self.damage.

                original_damage = float(self.DAMAGE)
                if is_critical:
                    self.damage = original_damage * 3.0
                else:
                    self.damage = original_damage

                # To actually deal damage if world was passed, we can't. We just set the flag so Action can use it, or we rely on action.py
                # Let's just set self.attack_timer
                self.attack_timer = float(max(0.2, 2.0 / self.SPEED if self.SPEED > 0 else 1.0))

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
