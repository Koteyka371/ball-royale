from ai.game_modes import GameMode
from typing import List, Any
import random

class KineticReversalZoneMode(GameMode):
    """
    A mode featuring a Kinetic Reversal Zone hazard.
    Entities entering the zone have their velocity vectors flipped 180 degrees.
    """

    class KineticReversalZoneHazard:
        def __init__(self, id_val: int, x: float, y: float, radius: float = 150.0):
            self.id = id_val
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = "kinetic_reversal_zone"
            self.damage = 0.0
            self.active = True
            self.duration = 15.0

    def __init__(self):
        super().__init__()
        self.name = "Kinetic Reversal Zone"
        self.zone_spawn_timer = 0.0
        self.zone_spawn_interval = 5.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)

    def tick(self, world: Any, balls: List[Any], delta: float) -> None:
        super().tick(world, balls, delta)

        self.zone_spawn_timer -= delta
        if self.zone_spawn_timer <= 0:
            self.zone_spawn_timer = self.zone_spawn_interval

            # Spawn a zone
            x = random.uniform(100, 700)
            y = random.uniform(100, 500)
            hz = self.KineticReversalZoneHazard(world.next_id, x, y)
            world.next_id += 1
            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []
            world.arena.hazards.append(hz)
            if hasattr(world, "add_event"):
                world.add_event("kinetic_reversal_zone_spawned", {"x": x, "y": y, "radius": hz.radius})

        # Clean up expired zones
        if hasattr(world.arena, "hazards"):
            for h in world.arena.hazards[:]:
                if getattr(h, "kind", "") == "kinetic_reversal_zone":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            world.arena.hazards.remove(h)
                            if hasattr(world, "add_event"):
                                world.add_event("kinetic_reversal_zone_despawned", {"x": h.x, "y": h.y})

# Register the game mode
from ai.game_modes import GAME_MODES
GAME_MODES["kinetic_reversal_zone"] = KineticReversalZoneMode()
