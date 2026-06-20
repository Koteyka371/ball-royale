"""
Auto-generated ball type: Sniper
Long range killer, high damage, low HP
"""





import math
from ai.personality import Personality

class Sniper:
    BALL_TYPE = "sniper"
    HP = 70
    SPEED = 3.0
    DAMAGE = 30
    RADIUS = 9
    PERCEPTION_RADIUS = 500
    AGGRESSION = 0.6
    COLOR = "blue"
    SKILL = "precision_shot"
    SKILL_COOLDOWN = 6.0
    ATTACK_RANGE = 150.0

    def __init__(self, ball_id: int, x: float = 0.0, y: float = 0.0):
        self.id = ball_id
        self.hp = float(self.HP)
        self.max_hp = float(self.HP)
        self.x = x
        self.y = y
        self.alive = True
        self.kills = 0
        self.attack_timer: float = 0.0
        self.attack_range = float(self.ATTACK_RANGE)
        self.first_hit_taken = False
        self.current_action = "idle"
        self.skill_timer = 0.0
        self.personality = Personality("cautious")

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float) -> None:
        self.current_action = "flee"

    def attack(self, delta: float) -> None:
        self.current_action = "kite"

    def kite(self, delta: float, target=None) -> None:
        """Kite — держит дистанцию, атакует при приближении skill: для Sniper"""
        self.current_action = "kite"
        if target is None:
            return

        dx_target = target.x - self.x
        dy_target = target.y - self.y
        distance_val = math.hypot(dx_target, dy_target)

        if distance_val > 0.0001:
            dir_x = dx_target / distance_val
            dir_y = dy_target / distance_val
            move_step = self.SPEED * delta * 60.0

            # Maintain distance logic
            if distance_val > self.attack_range:
                # Move closer if too far
                approach_dist = min(move_step, distance_val - self.attack_range)
                self.x += dir_x * approach_dist
                self.y += dir_y * approach_dist
            elif distance_val < self.attack_range * 0.8:
                # Retreat if too close
                self.x -= dir_x * move_step
                self.y -= dir_y * move_step

            # Update distance post-movement
            new_dx_target = target.x - self.x
            new_dy_target = target.y - self.y
            new_distance_val = math.hypot(new_dx_target, new_dy_target)

            # Attack logic when in range
            if new_distance_val <= self.attack_range:
                if new_distance_val < self.attack_range * 0.8 and self.skill_timer <= 0:
                    self.use_skill()
                if getattr(self, 'attack_timer', 0.0) <= 0:
                    self.attack_timer = max(0.2, 2.0 / self.SPEED if self.SPEED > 0 else 1.0)

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
