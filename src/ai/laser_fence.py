from ai.game_modes import GameMode
import random

class LaserFenceMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Laser Fence"
        self.description = "Hazard lines periodically spawn and move across the arena, damaging anyone caught."
        self.spawn_timer = 0.0
        self.spawn_interval = 5.0
        self.fence_speed = 100.0
        self.fence_damage_per_second = 100.0
        self.fence_thickness = 20.0
        self.fences = []

    def setup(self, world, balls):
        super().setup(world, balls)
        self.spawn_timer = 0.0
        self.fences = []

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)

        arena_width = getattr(world.arena, "width", 1000)
        arena_height = getattr(world.arena, "height", 1000)

        self.spawn_timer += delta
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval

            orientation = random.choice(["horizontal", "vertical"])
            dir = random.choice([-1, 1])

            if orientation == "horizontal":
                pos = 0.0 if dir == 1 else arena_height
            else:
                pos = 0.0 if dir == 1 else arena_width

            self.fences.append({
                "orientation": orientation,
                "pos": pos,
                "dir": dir
            })

        active_fences = []
        for fence in self.fences:
            fence["pos"] += self.fence_speed * delta * fence["dir"]

            if fence["orientation"] == "horizontal":
                if -100 <= fence["pos"] <= arena_height + 100:
                    active_fences.append(fence)
            else:
                if -100 <= fence["pos"] <= arena_width + 100:
                    active_fences.append(fence)

        self.fences = active_fences

        for fence in self.fences:
            for b in balls:
                if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                    continue

                b_x = getattr(b, "x", 0.0)
                b_y = getattr(b, "y", 0.0)

                hit = False
                if fence["orientation"] == "horizontal":
                    if abs(b_y - fence["pos"]) < self.fence_thickness:
                        hit = True
                else:
                    if abs(b_x - fence["pos"]) < self.fence_thickness:
                        hit = True

                if hit:
                    hp = getattr(b, "hp", 100.0)
                    hp -= self.fence_damage_per_second * delta
                    if hp <= 0:
                        hp = 0
                        setattr(b, "alive", False)
                    setattr(b, "hp", hp)
