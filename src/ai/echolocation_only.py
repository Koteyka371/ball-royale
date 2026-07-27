from ai.game_modes import GameMode, GAME_MODES
from typing import Any, List

class EcholocationOnlyMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Echolocation Only"
        self.description = "Players cannot see the arena except for a tiny radius. Every few seconds, players emit a sound pulse that reveals enemies and walls momentarily."
        self.pulse_timer = 0.0
        self.pulse_interval = 4.0
        self.is_pulsing = False
        self.pulse_duration = 0.5
        self.current_pulse_time = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.pulse_timer = 0.0
        self.is_pulsing = False
        self.current_pulse_time = 0.0

        if hasattr(world, "arena") and world.arena:
            world.arena.is_night = True

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.base_perception_radius = getattr(b, "perception_radius", 250.0)
                b.perception_radius = 15.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        self.pulse_timer += delta

        if self.is_pulsing:
            self.current_pulse_time += delta
            if self.current_pulse_time >= self.pulse_duration:
                self.is_pulsing = False
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                        b.perception_radius = 15.0
        else:
            if self.pulse_timer >= self.pulse_interval:
                self.pulse_timer = 0.0
                self.is_pulsing = True
                self.current_pulse_time = 0.0

                if hasattr(world, "add_event"):
                    world.add_event("sound_pulse", {"type": "sound_pulse", "message": "Sound pulse reveals the arena!"})

                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                        b.perception_radius = getattr(b, "base_perception_radius", 250.0)

GAME_MODES['echolocation_only'] = EcholocationOnlyMode()
