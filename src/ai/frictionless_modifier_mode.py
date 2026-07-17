from typing import Any, List
try:
    from .game_modes import GameMode
except ImportError:
    class GameMode:
        def setup(self, world: Any, balls: List[Any]) -> None:
            pass
        def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
            pass
import random

class FrictionlessArenaModifierMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Frictionless Arena Modifier"
        self.description = "Introduces an arena modifier that completely removes friction for a random duration, forcing players to perfectly balance their momentum and making collisions much more impactful and chaotic."
        self.frictionless_active = False
        self.timer = random.uniform(10.0, 30.0)
        self.event_message_sent = False

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.frictionless_active = False
        self.timer = random.uniform(10.0, 30.0)
        self.event_message_sent = True # Don't send initial "inactive" event

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        self.timer -= delta

        if self.timer <= 0:
            self.frictionless_active = not self.frictionless_active
            self.event_message_sent = False
            if self.frictionless_active:
                # Active for 5 to 15 seconds
                self.timer = random.uniform(5.0, 15.0)
            else:
                # Inactive for 10 to 30 seconds
                self.timer = random.uniform(10.0, 30.0)

        if self.frictionless_active:
            if not self.event_message_sent:
                if hasattr(world, "add_event"):
                    world.add_event("frictionless_modifier", {"message": "The arena is now completely frictionless! Balance your momentum!"})
                self.event_message_sent = True

            for b in balls:
                if getattr(b, "alive", False):
                    b.is_frictionless = True
        else:
            if not self.event_message_sent:
                if hasattr(world, "add_event"):
                    world.add_event("frictionless_modifier", {"message": "Friction has returned to normal."})
                self.event_message_sent = True

            for b in balls:
                if getattr(b, "alive", False):
                    b.is_frictionless = False
