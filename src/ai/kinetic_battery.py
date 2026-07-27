from ai.game_modes import GameMode
import random

class KineticBatteryMode(GameMode):
    def setup(self, world, balls):
        self.arena_width = getattr(world.arena, 'width', 800) if hasattr(world, 'arena') else 800
        self.arena_height = getattr(world.arena, 'height', 600) if hasattr(world, 'arena') else 600

    def tick(self, world, balls, delta=0.016):
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                continue

            # Balls don't do damage directly
            b.damage = 0.0
            b.base_damage = 0.0

            # Initialize battery variables
            charge = getattr(b, "kinetic_charge", 0.0)

            vx = getattr(b, "vx", 0.0)
            vy = getattr(b, "vy", 0.0)
            speed_sq = vx*vx + vy*vy
            speed = speed_sq ** 0.5

            # Charge based on movement speed
            charge += speed * delta * 0.1 # Example charge rate

            # Detect bounces
            radius = getattr(b, "radius", 15.0)
            x = getattr(b, "x", 0.0)
            y = getattr(b, "y", 0.0)
            prev_vx = getattr(b, "meta_prev_vx", vx)
            prev_vy = getattr(b, "meta_prev_vy", vy)

            bounced = False
            if (x <= radius or x >= self.arena_width - radius) and vx * prev_vx < 0:
                bounced = True
            if (y <= radius or y >= self.arena_height - radius) and vy * prev_vy < 0:
                bounced = True

            if bounced:
                charge += 20.0 # Burst charge on bounce

            b.meta_prev_vx = vx
            b.meta_prev_vy = vy

            if charge >= 100.0:
                charge = 0.0
                # Unleash shockwave
                if hasattr(world, "add_event"):
                    world.add_event("explosion", {
                        "x": x, "y": y,
                        "radius": 200.0,
                        "damage": 100.0,
                        "color": "cyan"
                    })

                # Damage nearby enemies
                for other in balls:
                    if not getattr(other, "alive", False) or getattr(other, "ball_type", "") == "spectator" or other == b:
                        continue
                    if getattr(other, "team", "") != getattr(b, "team", ""):
                        ox = getattr(other, "x", 0.0)
                        oy = getattr(other, "y", 0.0)
                        dist_sq = (x - ox)**2 + (y - oy)**2
                        if dist_sq <= 200.0 * 200.0:
                            hp = getattr(other, "hp", 100.0)
                            other.hp = hp - 100.0
                            if other.hp <= 0:
                                other.alive = False

            b.kinetic_charge = charge
