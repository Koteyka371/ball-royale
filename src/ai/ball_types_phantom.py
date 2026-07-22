"""
Auto-generated ball type: Phantom
Can phase through enemies, hit and run
"""




from ai.personality import Personality

class Phantom:
    BALL_TYPE = "phantom"
    HP = 65
    SPEED = 3.0
    DAMAGE = 22
    RADIUS = 8
    PERCEPTION_RADIUS = 320
    AGGRESSION = 0.7
    COLOR = "cyan"
    SKILL = "phase_through"
    SKILL_COOLDOWN = 4.0

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
        self.personality = Personality("cunning")

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
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"
