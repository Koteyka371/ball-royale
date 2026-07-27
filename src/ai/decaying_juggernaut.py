from typing import Any, List, Optional
from ai.game_modes import GameMode

class DecayingJuggernautMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Decaying Juggernaut"
        self.description = "Similar to Juggernaut mode, but the Juggernaut's stats slowly decay over time, pushing players to stay aggressive and preventing endless stalling."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        if not valid_balls:
            return

        boss = valid_balls[0]
        self._make_juggernaut(world, boss)

        # The rest are hunters
        for b in valid_balls:
            if b == boss:
                continue
            b.team = "Hunters"
            if not hasattr(b, "base_max_hp"):
                b.base_max_hp = getattr(b, "max_hp", 100.0)
            b.max_hp = b.base_max_hp * 0.8
            b.hp = b.max_hp

    def _make_juggernaut(self, world: Any, b: Any) -> None:
        b.team = "Juggernaut"
        if not hasattr(b, "base_max_hp"):
            b.base_max_hp = getattr(b, "max_hp", 100.0)

        b.max_hp = b.base_max_hp * 10.0
        b.hp = b.max_hp

        if not hasattr(b, "base_damage"):
            b.base_damage = getattr(b, "damage", 10.0)
        b.damage = b.base_damage * 2.0

        if not hasattr(b, "base_radius"):
            b.base_radius = getattr(b, "radius", 10.0)
        b.radius = b.base_radius * 3.0

        b.base_speed = float(getattr(b, "base_speed", getattr(b, "speed", 100.0))) * 0.6

        if not hasattr(b, "base_mass"):
            b.base_mass = getattr(b, "mass", 1.0)
        b.mass = b.base_mass * 5.0

        b.juggernaut_decay = 1.0

        # fully heal
        b.hp = b.max_hp

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        # Check for Juggernaut death
        dead_juggernauts = [b for b in balls if getattr(b, "team", "") == "Juggernaut" and not getattr(b, "alive", False)]

        for dead_jug in dead_juggernauts:
            killer_id = getattr(dead_jug, "killer", None)
            if killer_id is not None:
                killer = next((b for b in balls if getattr(b, "id", None) == killer_id), None)
                if killer and getattr(killer, "alive", False):
                    self._make_juggernaut(world, killer)
                    if hasattr(world, "add_event"):
                        world.add_event("juggernaut_change", {"message": "A new Juggernaut has emerged!"})
            dead_jug.team = "Dead"
            if hasattr(dead_jug, "juggernaut_decay"):
                delattr(dead_jug, "juggernaut_decay")

        for b in balls:
            if getattr(b, "team", "") == "Juggernaut" and getattr(b, "alive", False):
                b.hp = min(b.hp + 5.0 * delta, getattr(b, "max_hp", 1000.0))

                decay_rate = 0.02 # 2% per second
                if not hasattr(b, "juggernaut_decay"):
                    b.juggernaut_decay = 1.0

                b.juggernaut_decay -= decay_rate * delta
                b.juggernaut_decay = max(0.2, b.juggernaut_decay)

                decay_mult = b.juggernaut_decay
                if hasattr(b, "base_max_hp"):
                    b.max_hp = b.base_max_hp * (1.0 + 9.0 * decay_mult)
                    b.hp = min(b.hp, b.max_hp)

                if hasattr(b, "base_damage"):
                    b.damage = b.base_damage * (1.0 + 1.0 * decay_mult)

                if hasattr(b, "base_radius"):
                    b.radius = b.base_radius * (1.0 + 2.0 * decay_mult)

                if hasattr(b, "base_mass"):
                    b.mass = b.base_mass * (1.0 + 4.0 * decay_mult)

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) not in ["spectator", "shadow_monster"]]
        if not alive:
            return "Draw"

        juggernaut_alive = any(getattr(b, "team", "") == "Juggernaut" for b in alive)
        hunters_alive = any(getattr(b, "team", "") == "Hunters" for b in alive)

        if not juggernaut_alive:
            return "Hunters"
        if not hunters_alive:
            return "Juggernaut"

        return None
