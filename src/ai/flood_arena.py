from typing import Any, List
from ai.game_modes import GameMode

class FloodArenaMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Flood Arena"
        self.description = "The arena is submerged in deep water, reducing movement speed and perception for non-aquatic balls. Periodically, giant whirlpools spawn, dragging players into the center. Find buoyant floating debris to regain normal speed and stamina."
        self.whirlpool_timer = 0.0
        self.whirlpool_spawn_interval = 20.0
        self.debris_timer = 0.0
        self.debris_spawn_interval = 15.0
        self.water_slow_factor = 0.4
        self.water_perception_factor = 0.5
        import random
        self.random = random

    def tick(self, world: Any, balls: List[Any], delta: float) -> None:
        super().tick(world, balls, delta)

        # Apply water debuffs to non-aquatic balls
        for b in balls:
            if not getattr(b, 'alive', True):
                continue

            # Check if they have floating debris buff
            has_debris = getattr(b, 'has_floating_debris', False)
            debris_timer = getattr(b, 'floating_debris_timer', 0.0)

            if has_debris and debris_timer > 0:
                b.floating_debris_timer -= delta
                if b.floating_debris_timer <= 0:
                    b.has_floating_debris = False

            is_aquatic = getattr(b, 'type', '') == 'aquatic'

            # Apply debuff if not aquatic and no debris buff
            if not is_aquatic and not getattr(b, 'has_floating_debris', False):
                if not hasattr(b, 'base_speed'):
                    b.base_speed = getattr(b, 'speed', 10.0)
                if not hasattr(b, 'base_perception_radius'):
                    b.base_perception_radius = getattr(b, 'perception_radius', 100.0)

                b.speed = b.base_speed * self.water_slow_factor
                b.perception_radius = b.base_perception_radius * self.water_perception_factor
            else:
                # Restore base stats if aquatic or has debris
                if hasattr(b, 'base_speed'):
                    b.speed = b.base_speed
                if hasattr(b, 'base_perception_radius'):
                    b.perception_radius = b.base_perception_radius

        # Spawn debris
        self.debris_timer += delta
        if self.debris_timer >= self.debris_spawn_interval:
            self.debris_timer = 0.0
            self._spawn_debris(world)

        # Spawn whirlpool
        self.whirlpool_timer += delta
        if self.whirlpool_timer >= self.whirlpool_spawn_interval:
            self.whirlpool_timer = 0.0
            self._spawn_whirlpool(world)

        # Update existing whirlpools
        if hasattr(world, 'hazards'):
            for h in list(world.hazards):
                if getattr(h, 'kind', '') == 'whirlpool':
                    if hasattr(h, 'update'):
                        h.update(delta, balls, world)
                    else:
                        life = getattr(h, 'life', 0)
                        life -= delta
                        if life <= 0:
                            h['active'] = False if isinstance(h, dict) else setattr(h, 'active', False)
                            world.hazards.remove(h)
                        else:
                            if isinstance(h, dict): h['life'] = life
                            else: h.life = life

                            for b in balls:
                                if not getattr(b, 'alive', True): continue
                                dx = (h['x'] if isinstance(h, dict) else h.x) - getattr(b, 'x', 0)
                                dy = (h['y'] if isinstance(h, dict) else h.y) - getattr(b, 'y', 0)
                                dist = (dx**2 + dy**2)**0.5
                                radius = h['radius'] if isinstance(h, dict) else getattr(h, 'radius', 150)
                                if 0 < dist < radius:
                                    strength = h['pull_strength'] if isinstance(h, dict) else getattr(h, 'pull_strength', 150)
                                    force = strength * (1.0 - dist / radius)
                                    b.x += (dx / dist) * force * delta
                                    b.y += (dy / dist) * force * delta


    def _spawn_debris(self, world: Any) -> None:
        if not hasattr(world, 'boosters'):
            return

        class FloatingDebris:
            def __init__(self, x, y):
                self.x = x
                self.y = y
                self.type = 'floating_debris'
                self.radius = 15.0
                self.active = True

            def collect(self, ball):
                ball.has_floating_debris = True
                ball.floating_debris_timer = 10.0
                if hasattr(ball, 'stamina'):
                    ball.stamina = getattr(ball, 'max_stamina', 100.0)
                self.active = False

        arena = getattr(world, 'arena', None)
        max_x = getattr(arena, 'width', 800.0) if arena else 800.0
        max_y = getattr(arena, 'height', 600.0) if arena else 600.0

        x = self.random.uniform(50, max_x - 50)
        y = self.random.uniform(50, max_y - 50)

        world.boosters.append(FloatingDebris(x, y))

    def _spawn_whirlpool(self, world: Any) -> None:
        if not hasattr(world, 'hazards'):
            return

        class Whirlpool:
            def __init__(self, x, y):
                self.x = x
                self.y = y
                self.kind = 'whirlpool'
                self.radius = 150.0
                self.pull_strength = 150.0
                self.active = True
                self.life = 10.0

            def update(self, delta, balls, world):
                self.life -= delta
                if self.life <= 0:
                    self.active = False
                    return

                for b in balls:
                    if not getattr(b, 'alive', True):
                        continue

                    dx = self.x - getattr(b, 'x', 0)
                    dy = self.y - getattr(b, 'y', 0)
                    dist = (dx**2 + dy**2)**0.5

                    if 0 < dist < self.radius:
                        # Pull them in
                        force = self.pull_strength * (1.0 - dist / self.radius)
                        b.x += (dx / dist) * force * delta
                        b.y += (dy / dist) * force * delta

        arena = getattr(world, 'arena', None)
        max_x = getattr(arena, 'width', 800.0) if arena else 800.0
        max_y = getattr(arena, 'height', 600.0) if arena else 600.0

        x = self.random.uniform(150, max_x - 150)
        y = self.random.uniform(150, max_y - 150)

        world.hazards.append(Whirlpool(x, y))
