"""
Auto-generated ball type: Sniper
Long range killer, high damage, low HP
"""





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

        import math
        dx = target.x - self.x
        dy = target.y - self.y
        dist_sq = dx * dx + dy * dy
        if dist_sq > 0.0001:
            dist = math.sqrt(dist_sq)
            nx, ny = dx / dist, dy / dist

            # Keep distance
            if dist > self.attack_range:
                pass # Move closer (handled by Action layer globally, or we could add self.x += nx * speed)
            elif dist < self.attack_range * 0.8:
                # Move away
                step = self.SPEED * delta * 60.0
                self.x -= nx * step
                self.y -= ny * step

            # Attack when approached or in range
            if dist <= self.attack_range:
                if dist < self.attack_range * 0.8 and self.skill_timer <= 0:
                    self.use_skill()

                # Attacking logic is normally handled by world._deal_damage, we just signal it here
                if hasattr(self, 'attack_timer') and self.attack_timer <= 0:
                    # In true implementation, action.py deals damage
                    pass

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
