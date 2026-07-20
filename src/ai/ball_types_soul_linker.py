from ai.personality import Personality
import math

class SoulLinker:
    BALL_TYPE = "soul_linker"
    HP = 100
    SPEED = 3.5
    DAMAGE = 5
    RADIUS = 10
    PERCEPTION_RADIUS = 250
    AGGRESSION = 0.5
    COLOR = "magenta"
    SKILL = "soul_bond"
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
        self.personality = Personality("strategic")

        self.base_speed = float(self.SPEED)
        self.speed = float(self.SPEED)
        self.damage = float(self.DAMAGE)
        self.attack_range = 15.0

        self.linked_enemy = None
        self.has_linked = False
        self.attack_timer = 0.0

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float, target=None) -> None:
        self.current_action = "flee"

        # Link to the first enemy it tries to interact with
        if not self.has_linked and target is not None and getattr(target, "alive", False):
            self._link_to(target)

    def attack(self, delta: float, target=None) -> None:
        self.current_action = "attack"

        # Link to the first enemy it attacks
        if not self.has_linked and target is not None and getattr(target, "alive", False):
            self._link_to(target)

        if target is None:
            return

        dx = target.x - self.x
        dy = target.y - self.y
        dist_sq = dx * dx + dy * dy
        if dist_sq > 0.0001:
            dist = math.sqrt(dist_sq)
            nx = dx / dist
            ny = dy / dist
            step = self.speed * delta * 60.0

            self.x += nx * min(step, dist)
            self.y += ny * min(step, dist)

            target_radius = getattr(target, 'radius', 10.0)
            attack_range_dist = self.RADIUS + target_radius + 5

            if dist <= attack_range_dist:
                if self.attack_timer <= 0:
                    self.attack_timer = float(max(0.2, 2.0 / self.speed if self.speed > 0 else 1.0))

    def _link_to(self, target):
        self.linked_enemy = target
        self.has_linked = True

        # Pairs health and speed to an enemy at the start of the round
        self.max_hp = float(getattr(target, "max_hp", 100.0))
        self.hp = float(getattr(target, "hp", 100.0))

        target_base_speed = float(getattr(target, "base_speed", getattr(target, "speed", 100.0)))
        target_speed = float(getattr(target, "speed", 100.0))

        self.base_speed = target_base_speed
        self.speed = target_speed

    def defend(self, delta: float) -> None:
        self.current_action = "defend"

    def collect_booster(self, delta: float) -> None:
        self.current_action = "collect_booster"

    def idle(self, delta: float) -> None:
        self.current_action = "idle"

    def take_damage(self, amount: float) -> None:
        if getattr(self, "radiation_duration", 0.0) > 0:
            amount *= getattr(self, "radiation_multiplier", 1.5)

        # Distribute 50% damage to the linked enemy
        if self.linked_enemy and getattr(self.linked_enemy, "alive", False):
            distributed_amount = amount * 0.5
            amount = amount * 0.5

            # Avoid infinite recursive loop if somehow both are soul_linkers targeting each other
            if hasattr(self.linked_enemy, "take_damage") and getattr(self.linked_enemy, "ball_type", "") != "soul_linker":
                self.linked_enemy.take_damage(distributed_amount)
            else:
                self.linked_enemy.hp -= distributed_amount
                if self.linked_enemy.hp <= 0:
                    self.linked_enemy.alive = False

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
