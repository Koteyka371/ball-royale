try:
    from src.ai.game_modes import GameMode
except ImportError:
    try:
        from ai.game_modes import GameMode
    except ImportError:
        class GameMode:
            def __init__(self):
                pass
            def tick(self, world, balls, delta=0.016):
                pass

class MirrorWorldMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Mirror World"
        self.description = "Creates a temporary mirror version of the map."
        self.mirror_timer = 0.0
        self.is_mirrored = False
        self.mirror_duration = 5.0
        self.normal_duration = 10.0

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)
        self.mirror_timer += delta

        if not self.is_mirrored and self.mirror_timer >= self.normal_duration:
            self.is_mirrored = True
            self.mirror_timer = 0.0
            self._mirror_world(world, balls)
        elif self.is_mirrored and self.mirror_timer >= self.mirror_duration:
            self.is_mirrored = False
            self.mirror_timer = 0.0
            self._mirror_world(world, balls)

    def _mirror_world(self, world, balls):
        arena_width = getattr(world.arena, "width", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0
        center_x = arena_width / 2.0

        if hasattr(world, "arena") and world.arena:
            if hasattr(world.arena, "hazards"):
                for hazard in world.arena.hazards:
                    if hasattr(hazard, "x"):
                        hazard.x = center_x + (center_x - hazard.x)
                        if hasattr(hazard, "vx"):
                            hazard.vx = -hazard.vx

            if hasattr(world.arena, "boosters"):
                for booster in world.arena.boosters:
                    if hasattr(booster, "x"):
                        booster.x = center_x + (center_x - booster.x)
                        if hasattr(booster, "vx"):
                            booster.vx = -booster.vx

        if hasattr(world, "projectiles"):
            for p in world.projectiles:
                if hasattr(p, "x"):
                    p.x = center_x + (center_x - p.x)
                if hasattr(p, "vx"):
                    p.vx = -p.vx
                if hasattr(p, "target_x"):
                    p.target_x = center_x + (center_x - p.target_x)

        for b in balls:
            if hasattr(b, "x"):
                b.x = center_x + (center_x - b.x)
            if hasattr(b, "vx"):
                b.vx = -b.vx
