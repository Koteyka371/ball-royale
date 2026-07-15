"""
Auto-generated ball type: Spectator
Spectator mode, invisible to other balls, observes the battle.
"""



class Spectator:
    BALL_TYPE = "spectator"
    HP = 99999
    SPEED = 5.0
    DAMAGE = 0
    RADIUS = 5
    PERCEPTION_RADIUS = 1000
    AGGRESSION = 0.0
    COLOR = "white"
    SKILL = "observe"
    SKILL_COOLDOWN = 1.0
    CHEER_POINTS = 100

    def __init__(self, ball_id: int, x: float = 0.0, y: float = 0.0):
        self.id = ball_id
        self.hp = self.HP
        self.max_hp = self.HP
        self.x = x
        self.y = y
        self.alive = True
        self.kills = 0
        self.current_action = "idle"
        self.skill_timer = 0.0
        self.personality = "spectator"
        self.cheer_points = self.CHEER_POINTS
        try:
            from ui.heatmap.danger_grid_overlay import DangerGridOverlay  # type: ignore
            self.danger_overlay = DangerGridOverlay()
        except ImportError:
            self.danger_overlay = None

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

        self.hp -= int(amount)
        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.BALL_TYPE}#{self.id} HP={self.hp}/{self.max_hp} [{self.current_action}]"

    def observe(self, world) -> None:
        if hasattr(world, "arena") and hasattr(world.arena, "danger_grid"):
            if self.danger_overlay:
                self.danger_overlay.update_danger_grid(world.arena.danger_grid)
