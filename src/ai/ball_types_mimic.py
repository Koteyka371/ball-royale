from ai.personality import Personality

class Mimic:
    BALL_TYPE = "mimic"
    HP = 100
    SPEED = 2.0
    DAMAGE = 10
    RADIUS = 10
    PERCEPTION_RADIUS = 250
    AGGRESSION = 0.5
    COLOR = "magenta"
    SKILL = "mimic_clone"
    SKILL_COOLDOWN = 15.0

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
        self.personality = Personality("opportunist")

        self.base_speed = float(self.SPEED)
        self.speed = float(self.SPEED)
        self.damage = float(self.DAMAGE)
        self.attack_range = 15.0
        self.copied_skill = None
        self.mimic_targets: dict[int, float] = {}  # {target_id: time_spent_near}
        self.copy_duration_required = 3.0 # seconds of proximity needed

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def _copy_stats_from(self, enemy):
        # Slightly adjust stats to match (e.g. interpolate 50% towards target stats)
        target_max_hp = getattr(enemy, 'max_hp', 100)
        target_speed = getattr(enemy, 'SPEED', 2.0)
        if not hasattr(enemy, 'SPEED'):
             target_speed = getattr(enemy, 'speed', 2.0)

        target_damage = getattr(enemy, 'DAMAGE', 10.0)
        if not hasattr(enemy, 'DAMAGE'):
             target_damage = getattr(enemy, 'damage', 10.0)

        # Permanent increase but not fully copying
        self.max_hp = self.max_hp * 0.5 + target_max_hp * 0.5
        self.hp = self.hp * 0.5 + getattr(enemy, 'hp', target_max_hp) * 0.5
        self.base_speed = self.base_speed * 0.5 + target_speed * 0.5
        self.speed = self.base_speed
        self.damage = self.damage * 0.5 + target_damage * 0.5

        # Copy skill
        self.copied_skill = getattr(enemy, 'SKILL', None)
        if not self.copied_skill:
             self.copied_skill = getattr(enemy.__class__, 'SKILL', 'none')
        self.SKILL = self.copied_skill

    def process_mimicry(self, enemies, delta: float):
        if self.copied_skill:
            return # Already mimicked someone

        for e in enemies:
            dist_sq = (e.x - self.x)**2 + (e.y - self.y)**2
            if dist_sq < 2500: # distance 50
                if e.id not in self.mimic_targets:
                    self.mimic_targets[e.id] = 0.0
                self.mimic_targets[e.id] += delta

                if self.mimic_targets[e.id] >= self.copy_duration_required:
                    self._copy_stats_from(e)
                    break

            elif e.id in self.mimic_targets:
                self.mimic_targets[e.id] = max(0.0, self.mimic_targets[e.id] - delta * 0.5) # Decay slowly

    def notify_kill(self, victim):
        if not self.copied_skill:
             self._copy_stats_from(victim)

    def flee(self, delta: float) -> None:
        self.current_action = "flee"

    def attack(self, delta: float) -> None:
        if not self.copied_skill:
            self.current_action = "chase" # Hunt down enemies to mimic
        else:
            self.current_action = "attack"

    def defend(self, delta: float) -> None:
        self.current_action = "defend"

    def collect_booster(self, delta: float) -> None:
        self.current_action = "collect_booster"

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
        if self.skill_timer <= 0 and self.copied_skill:
            self.skill_timer = self.SKILL_COOLDOWN
            # We can just say it triggers the copied skill, action layer might use self.SKILL
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
