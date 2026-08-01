import random
from ai.game_modes import GameMode

class SignalScramblerMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Signal Scrambler Gadget"
        self.description = "A massive gadget at the center of the arena permanently scrambles homing missiles and drastically reduces AI perception in a large area."
        self.jammer_x = 0
        self.jammer_y = 0
        self.jammer_radius = 400.0
        self.setup_done = False

    def setup(self, world, balls):
        self.setup_done = False

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)

        if not hasattr(world, "arena"):
            return

        arena_width = getattr(world.arena, "width", 1000)
        arena_height = getattr(world.arena, "height", 1000)

        if not self.setup_done:
            self.jammer_x = arena_width / 2.0
            self.jammer_y = arena_height / 2.0
            self.setup_done = True

            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []

            try:
                from arena.procedural_arena import Hazard
                h = Hazard(id=len(world.arena.hazards) + 12000, x=self.jammer_x, y=self.jammer_y, radius=self.jammer_radius, kind="signal_scrambler", damage=0.0)
            except ImportError:
                class DummyJammer:
                    pass
                h = DummyJammer()
                h.id = len(world.arena.hazards) + 12000
                h.x = self.jammer_x
                h.y = self.jammer_y
                h.radius = self.jammer_radius
                h.kind = "signal_scrambler"
                h.damage = 0.0
                h.active = True

            world.arena.hazards.append(h)
