from typing import Any, List, Optional
from ai.game_modes import GameMode, WeatherAltarMixin

class DoubleJuggernautMode(GameMode, WeatherAltarMixin):
    def __init__(self):
        super().__init__()
        self.name = "Double Juggernaut"
        self.description = "Two players spawn as Juggernauts. When one is killed, they drop a massive heal, but the remaining Juggernaut gets an enrage buff."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.setup_altar(world)
        if not hasattr(world, "boosters"):
            world.boosters = []

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        if len(valid_balls) < 2:
            return

        juggernauts = valid_balls[:2]
        hunters = valid_balls[2:]

        for b in juggernauts:
            self._make_juggernaut(world, b)

        for b in hunters:
            b.team = "Hunters"
            if not hasattr(b, "base_max_hp"):
                b.base_max_hp = getattr(b, "max_hp", 100.0)
            b.max_hp = b.base_max_hp * 0.8
            b.hp = b.max_hp

    def _make_juggernaut(self, world: Any, b: Any) -> None:
        b.team = "Juggernaut"
        if not hasattr(b, "base_max_hp"):
            b.base_max_hp = getattr(b, "max_hp", 100.0)
        b.max_hp = b.base_max_hp * 5.0
        b.hp = b.max_hp

        if not hasattr(b, "base_damage"):
            b.base_damage = getattr(b, "damage", 10.0)
        b.damage = b.base_damage * 1.5

        if not hasattr(b, "base_radius"):
            b.base_radius = getattr(b, "radius", 10.0)
        b.radius = b.base_radius * 2.0

        if not hasattr(b, "base_speed"):
            b.base_speed = getattr(b, "speed", 100.0)
        b.speed = b.base_speed * 0.7

        if not hasattr(b, "base_mass"):
            b.base_mass = getattr(b, "mass", 1.0)
        b.mass = b.base_mass * 3.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        self.tick_altar(world, balls, delta)

        if not hasattr(world, "boosters"):
            world.boosters = []

        alive_juggernauts = []
        dead_juggernauts = []

        for b in balls:
            if getattr(b, "team", "") == "Juggernaut":
                if getattr(b, "alive", False):
                    alive_juggernauts.append(b)
                else:
                    dead_juggernauts.append(b)

        for b in dead_juggernauts:
            if not getattr(b, "dropped_heal", False):
                b.dropped_heal = True
                world.boosters.append({
                    "type": "massive_heal",
                    "x": getattr(b, "x", 0.0),
                    "y": getattr(b, "y", 0.0),
                    "value": 500.0
                })
                if hasattr(world, "add_event"):
                    world.add_event("juggernaut_death", {"message": "A Juggernaut has fallen and dropped a massive heal!"})

        if len(alive_juggernauts) == 1 and len(dead_juggernauts) >= 1:
            survivor = alive_juggernauts[0]
            if not getattr(survivor, "enraged", False):
                survivor.enraged = True
                survivor.damage = getattr(survivor, "base_damage", 10.0) * 3.0
                survivor.speed = getattr(survivor, "base_speed", 100.0) * 1.2
                survivor.radius = getattr(survivor, "base_radius", 10.0) * 2.5
                if hasattr(world, "add_event"):
                    world.add_event("juggernaut_enrage", {"message": "The remaining Juggernaut is enraged!"})

        for b in alive_juggernauts:
            b.hp = min(b.hp + 5.0 * delta, getattr(b, "max_hp", 1000.0))

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
