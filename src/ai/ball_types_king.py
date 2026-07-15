"""
Auto-generated ball type: King
Leader personality, stays behind allies, uses Command to buff team, targets low HP allies to boost, avoids direct combat.
"""



from ai.personality import Personality

class King:
    BALL_TYPE = "king"
    HP = 120
    SPEED = 4.0
    DAMAGE = 15
    RADIUS = 14
    PERCEPTION_RADIUS = 300
    AGGRESSION = 0.2
    COLOR = "gold"
    SKILL = "command"
    SKILL_COOLDOWN = 5.0

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
        self.attack_timer: float = 0.0
        self.personality = Personality("leader")

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

    def command(self, delta: float, target_ally=None) -> None:
        if hasattr(self, "attack_timer"):
            self.attack_timer -= delta
        if hasattr(self, "skill_timer"):
            self.skill_timer -= delta
        self.current_action = "defend"
        if target_ally is None:
            return

        import math

        # Calculate distance to ally
        dx = target_ally.x - self.x
        dy = target_ally.y - self.y
        dist_sq = dx * dx + dy * dy
        dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0

        # Movement towards ally
        target_radius = getattr(target_ally, "radius", 10.0)
        attack_range = self.RADIUS + target_radius + 5.0

        if dist > attack_range:
            nx = dx / dist if dist > 0 else 0
            ny = dy / dist if dist > 0 else 0
            step = self.SPEED * delta * 60.0
            self.x += nx * min(step, dist - attack_range * 0.8)
            self.y += ny * min(step, dist - attack_range * 0.8)

        # Recalculate distance after moving
        new_dx = target_ally.x - self.x
        new_dy = target_ally.y - self.y
        new_dist_sq = new_dx * new_dx + new_dy * new_dy
        new_dist = math.sqrt(new_dist_sq) if new_dist_sq > 0.0001 else 0.0

        # Command buff logic
        if new_dist <= attack_range:
            if getattr(self, "attack_timer", 0.0) <= 0.0:
                if self.skill_timer <= 0:
                    if hasattr(target_ally, "damage"):
                        target_ally.damage *= 1.2
                    if hasattr(target_ally, "speed"):
                        target_ally.speed *= 1.2
                    self.use_skill()

                speed = getattr(self, "speed", self.SPEED)
                cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                self.attack_timer = cooldown

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
