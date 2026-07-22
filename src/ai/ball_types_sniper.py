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
    SKILL = "snipe"
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

    def get_priority(self, target=None) -> str:
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > self.attack_range * 0.5:
                return "long_range_attack"
            else:
                return "flee"
        return "idle"

    def flee(self, delta: float) -> None:
        self.current_action = "flee"

    def attack(self, delta: float) -> None:
        self.current_action = "kite"

    def kite(self, delta: float, target=None) -> None:
        '''
        Kite — держит дистанцию, атакует при приближении skill: для Sniper
        '''
        self.current_action = "kite"

        if getattr(self, "skill_timer", 0.0) > 0:
            self.skill_timer -= delta
        if getattr(self, "attack_timer", 0.0) > 0:
            self.attack_timer -= delta

        if target is None:
            return

        diff_x = target.x - self.x
        diff_y = target.y - self.y
        dist = math.hypot(diff_x, diff_y)

        if dist <= 0.0001:
            return

        dir_x = diff_x / dist
        dir_y = diff_y / dist

        spd_move = self.SPEED * delta * 60.0
        safe_dist = self.attack_range * 0.8

        if dist > self.attack_range:
            m_step = min(spd_move, dist - self.attack_range)
            self.x += dir_x * m_step
            self.y += dir_y * m_step
        elif dist < safe_dist:
            self.x -= dir_x * spd_move
            self.y -= dir_y * spd_move

        new_dist = math.hypot(target.x - self.x, target.y - self.y)

        if new_dist <= self.attack_range:
            if getattr(self, "skill_timer", 0.0) <= 0:
                self.skill_timer = getattr(self, "SKILL_COOLDOWN", 6.0)
                self.current_action = "use_skill"
            elif getattr(self, "attack_timer", 0.0) <= 0:
                self.attack_timer = max(0.2, 2.0 / self.SPEED if self.SPEED > 0 else 1.0)
                self.current_action = "attack"

    def defend(self, delta: float) -> None:
        self.current_action = "defend"

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

        if self.hp <= 0 and getattr(self, "quantum_relay_timer", 0.0) > 0.0:
            self.hp = self.max_hp * 0.2
            self.x = getattr(self, "quantum_relay_x", self.x)
            self.y = getattr(self, "quantum_relay_y", self.y)
            self.quantum_relay_timer = 0.0
            if hasattr(self, "world") and hasattr(self.world, "events"):
                self.world.events.append({"type": "quantum_relay_triggered", "x": self.x, "y": self.y})
            return

        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN
            self.current_action = "use_skill"
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
# Cosmetics: kite behavior confirmed

# Cosmetic change to trigger a commit for auto-implement-kite-держит-дистанцию-атакует-при
