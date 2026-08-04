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
            self._spawn_shadows(world, balls)
        elif self.is_mirrored and self.mirror_timer >= self.mirror_duration:
            self.is_mirrored = False
            self.mirror_timer = 0.0
            self._mirror_world(world, balls)
            self._remove_shadows(world, balls)

        if self.is_mirrored:
            self._update_shadows(world, balls)

    def _spawn_shadows(self, world, balls):
        arena_width = getattr(world.arena, "width", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0
        center_x = arena_width / 2.0

        class MirrorShadow:
            def __init__(self, owner, cx):
                self.id = getattr(owner, "id", id(owner)) + 900000
                self.owner = owner
                self.x = cx + (cx - owner.x) if hasattr(owner, "x") else 0
                self.y = owner.y if hasattr(owner, "y") else 0
                self.vx = -owner.vx if hasattr(owner, "vx") else 0
                self.vy = owner.vy if hasattr(owner, "vy") else 0
                self.radius = getattr(owner, "radius", 15.0)
                self.hp = getattr(owner, "hp", 100.0)
                self.max_hp = getattr(owner, "max_hp", 100.0)
                self.last_hp = self.hp
                self.alive = True
                self.is_clone = True
                self.is_mirror_shadow = True
                self.team = getattr(owner, "team", "")
                self.color = "black"

        if not hasattr(self, "shadows"):
            self.shadows = []

        for b in balls:
            if not getattr(b, "alive", True) or getattr(b, "is_clone", False):
                continue
            shadow = MirrorShadow(b, center_x)
            self.shadows.append(shadow)
            if hasattr(world, "balls"):
                world.balls.append(shadow)

    def _remove_shadows(self, world, balls):
        if hasattr(self, "shadows"):
            for s in self.shadows:
                s.alive = False
            if hasattr(world, "balls"):
                world.balls = [b for b in world.balls if not getattr(b, "is_mirror_shadow", False)]
            self.shadows = []

    def _update_shadows(self, world, balls):
        arena_width = getattr(world.arena, "width", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0
        center_x = arena_width / 2.0

        if hasattr(self, "shadows"):
            for s in self.shadows:
                if not s.alive or not getattr(s.owner, "alive", True):
                    s.alive = False
                    continue

                if hasattr(s.owner, "x"):
                    s.x = center_x + (center_x - s.owner.x)
                if hasattr(s.owner, "y"):
                    s.y = s.owner.y
                if hasattr(s.owner, "vx"):
                    s.vx = -s.owner.vx
                if hasattr(s.owner, "vy"):
                    s.vy = s.owner.vy

                if s.hp < s.last_hp:
                    damage = s.last_hp - s.hp
                    s.owner.hp = max(0.0, getattr(s.owner, "hp", 100.0) - damage)
                    if s.owner.hp <= 0:
                        s.owner.alive = False

                s.hp = getattr(s.owner, "hp", s.hp)
                s.max_hp = getattr(s.owner, "max_hp", s.max_hp)
                s.last_hp = s.hp

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
