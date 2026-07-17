import math
import random

class SlingshotMode:
    def __init__(self):
        self.name = "Slingshot Mode"
        self.description = "Players can only move by dragging and releasing a slingshot mechanism, and deal damage based on speed upon collision with other players."

    def tick(self, world, balls, delta=0.016):
        # We simulate what GameMode.tick does, but it mostly does nothing unless overridden
        for b in balls:
            b.speed = 0.0
            if not hasattr(b, "slingshot_timer"):
                b.slingshot_timer = random.uniform(1.0, 3.0)
                b.slingshot_pulling = False

            if b.slingshot_pulling:
                b.slingshot_timer -= delta
                if b.slingshot_timer <= 0:
                    b.slingshot_pulling = False
                    b.slingshot_timer = random.uniform(1.0, 3.0)
                    angle = random.uniform(0, 2 * math.pi)
                    force = random.uniform(800.0, 1500.0)
                    b.vx = getattr(b, "vx", 0.0) + math.cos(angle) * force
                    b.vy = getattr(b, "vy", 0.0) + math.sin(angle) * force
            else:
                b.slingshot_timer -= delta
                if b.slingshot_timer <= 0:
                    b.slingshot_pulling = True
                    b.slingshot_timer = random.uniform(0.5, 1.5)

            vx = getattr(b, "vx", 0.0)
            vy = getattr(b, "vy", 0.0)
            speed_mag = math.hypot(vx, vy)
            b.damage = getattr(b, "base_damage", 10.0) + (speed_mag * 0.05)
