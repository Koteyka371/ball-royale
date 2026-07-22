"""
Auto-generated ball type: Necromancer
"""

import math
from ai.personality import Personality

class Necromancer:
    BALL_TYPE = "necromancer"
    HP = 90
    SPEED = 2.0
    DAMAGE = 15
    RADIUS = 10
    PERCEPTION_RADIUS = 320
    AGGRESSION = 0.3
    COLOR = 'black'
    SKILL = 'corpse_explosion'
    SKILL_COOLDOWN = 8.0
    ATTACK_RANGE = 35.0

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
        self.personality = Personality("aggressive")
        self.bone_armor_stacks = 0
        self.bone_armor_timer = 0.0

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

            self.x += nx * min(step, dist)
            self.y += ny * min(step, dist)

            target_radius = getattr(target, 'radius', 10.0)
            attack_range = self.RADIUS + target_radius + 5

            new_dx = target.x - self.x
            new_dy = target.y - self.y
            new_dist_sq = new_dx * new_dx + new_dy * new_dy
            new_dist = math.sqrt(new_dist_sq) if new_dist_sq > 0.0001 else 0.0

            if new_dist <= attack_range:
                if self.attack_timer <= 0:
                    self.attack_timer = float(max(0.2, 2.0 / self.SPEED if self.SPEED > 0 else 1.0))

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

        # Apply bone armor mitigation
        if self.bone_armor_stacks > 0 and amount > 0:
            # Consume 1 stack to mitigate flat damage (e.g., up to 10 flat reduction)
            reduction = min(10.0, amount)
            amount -= reduction
            self.bone_armor_stacks -= 1

        if amount > 0 and self.hp - amount <= 0:
            # Fatal damage, check for minions
            world = getattr(self, "world", None)
            if not world and hasattr(self, "_cached_world"):
                world = self._cached_world

            if world and hasattr(world, "balls"):
                import math
                minions = [b for b in world.balls if getattr(b, "minion_owner", None) == self.id and getattr(b, "alive", True)]

                # Filter minions by range
                minions_in_range = []
                for m in minions:
                    m_x = getattr(m, "x", 0.0)
                    m_y = getattr(m, "y", 0.0)
                    dist = math.hypot(m_x - self.x, m_y - self.y)
                    if dist <= getattr(self, "PERCEPTION_RADIUS", 320):
                        minions_in_range.append(m)

                if minions_in_range:
                    # Find nearest
                    nearest = min(minions_in_range, key=lambda m: math.hypot(getattr(m, "x", 0.0) - self.x, getattr(m, "y", 0.0) - self.y))

                    # Redirect to nearest minion
                    if hasattr(nearest, "take_damage"):
                        nearest.take_damage(9999.0)
                    elif hasattr(nearest, "hp"):
                        nearest.hp = 0
                        nearest.alive = False

                    self.hp = 1.0 # leave necro at 1 hp instead of dying
                    return

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

    def tick(self, delta: float) -> None:
        if not self.alive:
            return
        self.bone_armor_timer += delta
        while self.bone_armor_timer >= 5.0:  # Periodically generate
            self.bone_armor_timer -= 5.0
            if getattr(self, 'bone_armor_stacks', 0) < 5:  # Max 5 stacks
                self.bone_armor_stacks = getattr(self, 'bone_armor_stacks', 0) + 1

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
