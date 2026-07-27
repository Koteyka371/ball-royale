import math
from ai.game_modes import GameMode

class RicochetMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Ricochet Mode"
        self.description = "All projectiles bounce off walls infinitely until they hit a target or their duration expires, making positioning extremely important."

    def tick(self, world, balls, delta):
        super().tick(world, balls, delta)

        arena_width = getattr(getattr(world, "arena", None), "width", 1000)
        arena_height = getattr(getattr(world, "arena", None), "height", 1000)

        for proj in getattr(world, "projectiles", []) + getattr(getattr(world, "arena", None), "hazards", []):
            if not getattr(proj, "alive", True) or getattr(proj, "hp", 1.0) <= 0:
                continue

            b_type = getattr(proj, "ball_type", getattr(proj, "kind", ""))
            is_proj = b_type in ["projectile", "spell", "fireball", "bullet", "snipe", "laser_beam"] or getattr(proj, "is_projectile", False) or getattr(proj, "is_spell", False)

            if not is_proj:
                continue

            # Ensure infinite bounces by resetting/increasing bounces
            if hasattr(proj, "bounces"):
                proj.bounces = 0
            if hasattr(proj, "bounces_left"):
                proj.bounces_left = 999

            x = getattr(proj, "x", 0)
            y = getattr(proj, "y", 0)
            radius = getattr(proj, "radius", 5.0)
            vx = getattr(proj, "vx", 0)
            vy = getattr(proj, "vy", 0)

            bounced = False

            # Simple wall bounce logic for projectiles
            if x - radius < 0 and vx < 0:
                proj.vx = -vx
                proj.x = radius
                bounced = True
            elif x + radius > arena_width and vx > 0:
                proj.vx = -vx
                proj.x = arena_width - radius
                bounced = True

            if y - radius < 0 and vy < 0:
                proj.vy = -vy
                proj.y = radius
                bounced = True
            elif y + radius > arena_height and vy > 0:
                proj.vy = -vy
                proj.y = arena_height - radius
                bounced = True
