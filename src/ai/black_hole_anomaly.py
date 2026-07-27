import math
from ai.game_modes import GameMode

class BlackHoleAnomalyMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Black Hole Anomaly"
        self.description = "Periodically, a massive gravity well appears that sucks in projecticles and items, changing weapon trajectories and creating a dangerous pull effect."

        self.anomaly_timer = 10.0
        self.active_timer = 0.0
        self.active = False
        self.x = 500.0
        self.y = 500.0
        self.radius = 300.0
        self.pull_strength = 200.0

        self.random = __import__('random')

    def setup(self, world, balls):
        super().setup(world, balls)
        self.anomaly_timer = 10.0
        self.active_timer = 0.0
        self.active = False
        if hasattr(self, "random") and hasattr(world, "arena"):
            arena_width = getattr(world.arena, "width", 1000)
            arena_height = getattr(world.arena, "height", 1000)
            self.x = self.random.uniform(200, arena_width - 200)
            self.y = self.random.uniform(200, arena_height - 200)

    def tick(self, world, balls, delta=0.016):
        if not self.active:
            self.anomaly_timer -= delta
            if self.anomaly_timer <= 0:
                self.active = True
                self.active_timer = 5.0

                arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") else 1000
                arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") else 1000
                self.x = self.random.uniform(200, arena_width - 200)
                self.y = self.random.uniform(200, arena_height - 200)

                if hasattr(world, "add_event"):
                    world.add_event("anomaly_spawn", {"message": "A Black Hole Anomaly has appeared!"})
        else:
            self.active_timer -= delta
            if self.active_timer <= 0:
                self.active = False
                self.anomaly_timer = 10.0
                if hasattr(world, "add_event"):
                    world.add_event("anomaly_despawn", {"message": "The Black Hole Anomaly has dissipated."})
                return

            # Apply pull
            entities = []
            if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                entities.extend(world.arena.hazards)
            if hasattr(world, "boosters"):
                entities.extend(world.boosters)
            if hasattr(world, "projectiles"):
                entities.extend(world.projectiles)
            for b in balls:
                if getattr(b, "ball_type", "") == "projectile":
                    entities.append(b)

            for entity in entities:
                ex = None
                ey = None
                if isinstance(entity, dict):
                    ex = entity.get("x", 0)
                    ey = entity.get("y", 0)
                else:
                    ex = getattr(entity, "x", 0)
                    ey = getattr(entity, "y", 0)

                dx = self.x - ex
                dy = self.y - ey
                dist = math.sqrt(dx*dx + dy*dy)

                if 0 < dist < self.radius:
                    pull_force = (self.pull_strength * (1.0 - (dist / self.radius))) * delta

                    if isinstance(entity, dict):
                        if "vx" in entity:
                            entity["vx"] += (dx / dist) * pull_force
                            entity["vy"] += (dy / dist) * pull_force
                        else:
                            entity["x"] += (dx / dist) * pull_force
                            entity["y"] += (dy / dist) * pull_force
                    else:
                        if hasattr(entity, "vx") and hasattr(entity, "vy"):
                            entity.vx += (dx / dist) * pull_force
                            entity.vy += (dy / dist) * pull_force
                        else:
                            entity.x += (dx / dist) * pull_force
                            entity.y += (dy / dist) * pull_force
