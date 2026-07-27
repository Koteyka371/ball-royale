from ai.game_modes import GameMode

class EcholocationOnlyMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Echolocation Only"
        self.description = "Players cannot see the arena except for a tiny radius. Every few seconds, players emit a sound pulse that reveals enemies and walls momentarily."
        self.echolocation_timer = 0.0
        self.pulse_interval = 3.0
        self.pulse_duration = 0.5

    def setup(self, world, balls):
        super().setup(world, balls)
        self.echolocation_timer = 0.0

        for b in balls:
            if getattr(b, "ball_type", None) == "spectator":
                continue
            if not hasattr(b, "base_perception_radius"):
                b.base_perception_radius = getattr(b, "perception_radius", 250.0)
            b.perception_radius = 50.0

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)

        self.echolocation_timer += delta

        if self.echolocation_timer > (self.pulse_interval + self.pulse_duration):
            self.echolocation_timer = 0.0

        is_pulsing = self.echolocation_timer > self.pulse_interval

        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            if is_pulsing:
                b.perception_radius = 1000.0
            else:
                b.perception_radius = 50.0
