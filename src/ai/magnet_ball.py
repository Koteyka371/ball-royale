import math
import random
from ai.game_modes import GameMode

class MagnetizerHazard:
    def __init__(self, x=500.0, y=500.0):
        self.kind = "magnetizer"
        self.x = x
        self.y = y
        self.radius = 50.0
        self.damage = 0.0
        self.id = id(self)

    def to_dict(self):
        return {
            "kind": self.kind,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "damage": self.damage
        }

class MagnetBallMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Magnet Ball"
        self.description = "Players get magnetized with positive or negative charges. Opposite charges attract and same charges repel."
        self.pulse_timer = 0.0

    def setup(self, world, balls):
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []

        has_magnetizer = any(getattr(h, "kind", "") == "magnetizer" for h in world.arena.hazards)
        if not has_magnetizer:
            world.arena.hazards.append(MagnetizerHazard(500.0, 500.0))

    def apply_dynamic_traits(self, world, balls, delta):
        super().apply_dynamic_traits(world, balls, delta)

        # Check pulse timer for re-rolling charges
        self.pulse_timer += delta
        if self.pulse_timer > 5.0:
            self.pulse_timer = 0.0
            for b in balls:
                if getattr(b, "alive", True) and getattr(b, "ball_type", "") != "spectator":
                    b.magnet_charge = random.choice([-1, 1])
                    if hasattr(world, "add_event"):
                        world.add_event("magnet_charge_changed", {"ball_id": getattr(b, "id", 0), "charge": b.magnet_charge})

        # Ensure everyone has a charge
        for b in balls:
            if getattr(b, "alive", True) and getattr(b, "ball_type", "") != "spectator":
                if not hasattr(b, "magnet_charge"):
                    b.magnet_charge = random.choice([-1, 1])

        # Apply forces between balls
        for i in range(len(balls)):
            b1 = balls[i]
            if not getattr(b1, "alive", True) or getattr(b1, "ball_type", "") == "spectator":
                continue

            for j in range(i + 1, len(balls)):
                b2 = balls[j]
                if not getattr(b2, "alive", True) or getattr(b2, "ball_type", "") == "spectator":
                    continue

                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist = math.hypot(dx, dy)

                if 0 < dist < 400.0:
                    c1 = getattr(b1, "magnet_charge", 0)
                    c2 = getattr(b2, "magnet_charge", 0)

                    if c1 == 0 or c2 == 0:
                        continue

                    force = 500.0 * (1.0 - dist / 400.0) * delta

                    # opposite attract, same repel
                    if c1 == c2: # repel
                        fx = -dx / dist * force
                        fy = -dy / dist * force
                    else: # attract
                        fx = dx / dist * force
                        fy = dy / dist * force

                    b1.x += fx
                    b1.y += fy
                    b2.x -= fx
                    b2.y -= fy

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)
