import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

anomaly_class = """
class PhysicsAnomalyEventMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Physics Anomaly Event"
        self.description = "A random event that alters the physics of the arena. Projectiles curve, movement speed is affected depending on the direction of travel relative to the anomaly's center."
        self.event_timer = 0.0
        self.event_active = False
        self.event_duration = 0.0
        self.cx = 500.0
        self.cy = 500.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        if not self.event_active:
            self.event_timer += delta

        if not self.event_active and self.event_timer > 20.0:
            import random
            if random.random() < 0.2:  # 20% chance every 20s
                self.event_active = True
                self.event_duration = 15.0
                self.event_timer = 0.0
                if hasattr(world, "add_event"):
                    world.add_event("physics_anomaly", {"active": True, "message": "Physics Anomaly detected! Projectiles curve and movement is distorted!"})
            else:
                self.event_timer = 0.0

        if hasattr(world, "arena"):
            self.cx = getattr(world.arena, "width", 1000.0) / 2.0
            self.cy = getattr(world.arena, "height", 1000.0) / 2.0

        if self.event_active:
            self.event_duration -= delta
            if self.event_duration <= 0:
                self.event_active = False
                self.event_timer = 0.0
                if hasattr(world, "add_event"):
                    world.add_event("physics_anomaly", {"active": False})

            import math
            for b in balls:
                if not getattr(b, "alive", True) or getattr(b, "ball_type", None) == "spectator":
                    continue
                # Calculate vector to center
                dx = self.cx - getattr(b, "x", self.cx)
                dy = self.cy - getattr(b, "y", self.cy)
                dist = math.sqrt(dx*dx + dy*dy)

                # Check movement direction
                vx = getattr(b, "vx", 0.0)
                vy = getattr(b, "vy", 0.0)
                speed_sq = vx*vx + vy*vy
                if speed_sq > 0.01 and dist > 0.01:
                    # Normalize
                    ndx = dx / dist
                    ndy = dy / dist
                    nvx = vx / math.sqrt(speed_sq)
                    nvy = vy / math.sqrt(speed_sq)

                    dot = ndx * nvx + ndy * nvy

                    # Dot > 0 means moving towards center.
                    # Speed increases when moving towards center, decreases when moving away.
                    speed_mod = 1.0 + (dot * 0.5) # Modifies speed by +/- 50%
                    b.physics_anomaly_speed_mod = speed_mod
                else:
                    b.physics_anomaly_speed_mod = 1.0
        else:
            for b in balls:
                if hasattr(b, "physics_anomaly_speed_mod"):
                    delattr(b, "physics_anomaly_speed_mod")
"""

# Find the place to insert it. Just before `GAME_MODES = {`
content = content.replace("GAME_MODES = {", anomaly_class + "\nGAME_MODES = {")
content = content.replace('"reverse_gravity_event": ReverseGravityEventMode(),', '"reverse_gravity_event": ReverseGravityEventMode(),\n    "physics_anomaly_event": PhysicsAnomalyEventMode(),')

with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
print("Updated src/ai/game_modes.py")
